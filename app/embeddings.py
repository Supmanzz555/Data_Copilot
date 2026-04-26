"""
KB loader with heading-aware chunking and Jina Embeddings API (remote).
Chunks by markdown sections (##); embeddings are computed via HTTPS, not on the host CPU/GPU.
"""
import os
from sqlalchemy import text

from app.database import engine
from app.jina_client import embed_texts_sync

KB_DIR = os.path.join(os.path.dirname(__file__), "kb_docs")

# Batch size for API calls (many small chunks per request is fine; cap payload size)
_EMBED_BATCH_SIZE = 32


def chunk_text(text: str, chunk_size: int = 600) -> list[str]:
    """Heading-aware chunking that keeps sections together"""
    chunks = []
    lines = text.split("\n")

    current_chunk = ""
    current_heading = ""

    for line in lines:
        if line.startswith("##"):
            if current_chunk.strip():
                chunks.append(current_chunk.strip())

            current_heading = line + "\n"
            current_chunk = current_heading
        else:
            if line.strip():
                current_chunk += line + "\n"

            if len(current_chunk) > chunk_size and current_chunk != current_heading:
                chunks.append(current_chunk.strip())
                current_chunk = current_heading

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def load_kb_documents():
    """Load KB documents with chunking and Jina embeddings (retrieval.passage)."""
    from app.config import settings

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM kb_embeddings"))

        print(f"Loading & embedding KB documents from {KB_DIR} (Jina API, model={settings.JINA_EMBEDDINGS_MODEL})...")

        rows: list[tuple[str, str]] = []
        for file in os.listdir(KB_DIR):
            if not file.endswith(".md"):
                continue

            path = os.path.join(KB_DIR, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            chunks = chunk_text(content)
            print(f"  📄 {file}: {len(chunks)} chunks")
            for i, chunk in enumerate(chunks):
                rows.append((f"{file}_chunk{i+1}", chunk))

        total_chunks = 0
        for start in range(0, len(rows), _EMBED_BATCH_SIZE):
            batch = rows[start : start + _EMBED_BATCH_SIZE]
            doc_names = [r[0] for r in batch]
            texts = [r[1] for r in batch]
            embeddings = embed_texts_sync(texts, task="retrieval.passage")
            for doc_name, chunk, emb in zip(doc_names, texts, embeddings):
                try:
                    conn.execute(
                        text(
                            "INSERT INTO kb_embeddings (doc_name, content, embedding) VALUES (:doc, :content, :emb)"
                        ),
                        {"doc": doc_name, "content": chunk, "emb": emb},
                    )
                    total_chunks += 1
                except Exception as e:
                    print(f"Error storing chunk {doc_name}: {e}")

        print(f"\nSuccessfully loaded {total_chunks} chunks via Jina Embeddings API.")
        return total_chunks


if __name__ == "__main__":
    load_kb_documents()
