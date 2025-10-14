import logging
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy import text
from app.pii_masking import mask_pii_in_results

logger = logging.getLogger(__name__)

# aysnc for tools
engine: AsyncEngine = create_async_engine(
    "postgresql+asyncpg://admin:admin@db:5432/deep_insights",
    echo=True,
)

async def sql_query(query: str, params: dict = None):
    """Execute read-only SQL query with PII masking"""
    # READONLY
    query_clean = query.strip()
    query_upper = query_clean.upper()
    
    # NO SQL cmonment
    query_upper_no_comments = query_upper.split('--')[0].strip()
    
    # Allow SELECT and WITH (for CTEs)
    if not (query_upper_no_comments.startswith('SELECT') or query_upper_no_comments.startswith('WITH')):
        logger.error(f"Non-SELECT query attempted: {query_clean[:100]}")
        raise ValueError("Only SELECT queries are allowed")
    
    async with engine.begin() as conn:
        res = await conn.execute(text(query), params or {})
        # convert rows to dict for async
        results = [dict(row._mapping) for row in res]
        # PII masking before returning
        return mask_pii_in_results(results)

async def kb_search(question: str):
    """Semantic search using LOCAL vector similarity"""
    async with engine.begin() as conn:
        # check if embbed exist
        check = await conn.execute(text("SELECT embedding FROM kb_embeddings WHERE embedding IS NOT NULL LIMIT 1"))
        has_embeddings = check.fetchone() is not None
        
        if has_embeddings:
            # loccal embedding model for vector search
            try:
                from sentence_transformers import SentenceTransformer
                
                # load model
                model = SentenceTransformer('all-MiniLM-L6-v2')
                
                # get question embedding
                question_emb = model.encode(question, convert_to_numpy=True).tolist()
                
                # vector similarity search using cosine distance
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
                # similarity threshold (0.4 = min relevant)
                results = [dict(row._mapping) for row in res]
                return [r for r in results if r.get('similarity', 0) > 0.4][:3]
            except Exception as e:
                logger.warning(f"Vector search failed, falling back to text search: {e}")
        
        # fallback to text search
        q = f"%{question.lower()}%"
        res = await conn.execute(
            text("SELECT doc_name, content FROM kb_embeddings WHERE content ILIKE :q LIMIT 3"),
            {"q": q},
        )
        return [dict(row._mapping) for row in res]

async def kpi_top_root_causes():
    """Get top 5 root causes with percentages"""
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
