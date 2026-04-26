"""
MCP Tools - Database query tools with safety guardrails.
"""
import asyncio
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.config import settings
from app.jina_client import embed_texts_async
from app.pii_masking import mask_pii_in_results

logger = logging.getLogger(__name__)

# Query timeout in seconds
QUERY_TIMEOUT = 30

# Cache for embeddings check (avoid hitting DB every request)
_embedding_cache_loaded = None


def _get_async_engine() -> AsyncEngine:
    url = settings.DATABASE_URL
    async_url = url.replace("postgresql://", "postgresql+asyncpg://", 1) if url.startswith("postgresql://") else url
    return create_async_engine(async_url, pool_pre_ping=True, pool_size=3)


async def sql_query(query: str, params: dict = None):
    """Execute read-only SQL query with PII masking"""
    query_clean = query.strip()
    query_upper = query_clean.upper()
    query_upper_no_comments = query_upper.split("--")[0].strip()
    
    if not (query_upper_no_comments.startswith("SELECT") or query_upper_no_comments.startswith("WITH")):
        logger.error(f"Non-SELECT query attempted: {query_clean[:100]}")
        raise ValueError("Only SELECT queries are allowed")
    
    engine = _get_async_engine()
    try:
        async with asyncio.timeout(QUERY_TIMEOUT):
            async with engine.begin() as conn:
                res = await conn.execute(text(query), params or {})
                results = [dict(row._mapping) for row in res]
                return mask_pii_in_results(results)
    except asyncio.TimeoutError:
        raise ValueError(f"Query timed out after {QUERY_TIMEOUT} seconds")
    finally:
        await engine.dispose()

SIMILARITY_THRESHOLD = 0.4  # Configurable similarity threshold


async def kb_search(question: str):
    """Semantic search using Jina embeddings + pgvector similarity"""
    engine = _get_async_engine()
    try:
        async with engine.begin() as conn:
            check = await conn.execute(text("SELECT embedding FROM kb_embeddings WHERE embedding IS NOT NULL LIMIT 1"))
            has_embeddings = check.fetchone() is not None
            
            if has_embeddings:
                try:
                    vecs = await embed_texts_async([question], task="retrieval.query")
                    question_emb = vecs[0]
                    if len(question_emb) != settings.JINA_EMBEDDING_DIMENSION:
                        raise ValueError(
                            f"Embedding size mismatch: expected {settings.JINA_EMBEDDING_DIMENSION}, got {len(question_emb)}"
                        )

                    res = await conn.execute(
                        text("""
                            SELECT doc_name, content, 
                                   1 - (embedding <=> CAST(:qemb AS vector)) as similarity
                            FROM kb_embeddings 
                            WHERE embedding IS NOT NULL
                            ORDER BY embedding <=> CAST(:qemb AS vector)
                            LIMIT 5
                        """),
                        {"qemb": str(question_emb)}
                    )
                    results = [dict(row._mapping) for row in res]
                    return [r for r in results if r.get("similarity", 0) > SIMILARITY_THRESHOLD][:3]
                except Exception as e:
                    logger.warning(f"Vector search failed, falling back to text search: {e}")
            
            q = f"%{question.lower()}%"
            res = await conn.execute(
                text("SELECT doc_name, content FROM kb_embeddings WHERE content ILIKE :q LIMIT 3"),
                {"q": q},
            )
            return [dict(row._mapping) for row in res]
    finally:
        await engine.dispose()


async def kpi_top_root_causes():
    """Get top 5 root causes with percentages"""
    engine = _get_async_engine()
    try:
        async with engine.begin() as conn:
            res = await conn.execute(
                text("""
                    SELECT category, COUNT(*) AS count,
                           ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM tickets), 2) AS percentage
                    FROM tickets
                    WHERE status = 'open'
                    GROUP BY category ORDER BY count DESC LIMIT 5
                """)
            )
            return [dict(row._mapping) for row in res]
    finally:
        await engine.dispose()
