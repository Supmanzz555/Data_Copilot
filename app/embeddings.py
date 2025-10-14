"""
KB loader with HEADING-AWARE chunking & LOCAL embeddings
Uses sentence-transformers (runs locally, no API needed)
Chunks by markdown sections (##) to preserve context
Meets requirement: "Chunk & embed docs into a vector store (pgvector)"
"""
import os
from sqlalchemy import create_engine, text
from sentence_transformers import SentenceTransformer

KB_DIR = os.path.join(os.path.dirname(__file__), "kb_docs")

# model instance
_model = None

def get_embedding_model():
    """Load lightweight local embedding model (384 dimensions, ~22MB)"""
    global _model
    if _model is None:
        print("🔄 Loading embedding model (one-time, ~22MB download)...")
        # all-MiniLM-L6-v2 smol fast and fast XD
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Model loaded!")
    return _model

def chunk_text(text: str, chunk_size: int = 600) -> list[str]:
    """Heading-aware chunking that keeps sections together"""
    chunks = []
    lines = text.split('\n')
    
    current_chunk = ""
    current_heading = ""
    
    for line in lines:
        # find md head ##
        if line.startswith('##'):
            # save previous chunk if exists
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            
            # start new chunk with heading
            current_heading = line + "\n"
            current_chunk = current_heading
        else:
            # add line to current chunk
            if line.strip():  # skip empty lines within sections
                current_chunk += line + "\n"
            
            # if chunk too big spilt but save heading context
            if len(current_chunk) > chunk_size and current_chunk != current_heading:
                chunks.append(current_chunk.strip())
                # Start new chunk with same heading for continuity
                current_chunk = current_heading
    
    # Add final chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def get_embedding(text: str, model: SentenceTransformer) -> list[float]:
    """Get embedding from local model (runs on CPU, fast)"""
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()

def load_kb_documents():
    """Load KB documents with chunking & local embeddings"""
    from app.config import settings
    
    # Load local embedding model
    model = get_embedding_model()
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.begin() as conn:
        # schema use 384 dim size of the model max size
        
        # clear existing kb entries
        conn.execute(text("DELETE FROM kb_embeddings"))
        
        print(f"Loading & embedding KB documents from {KB_DIR}...")
        
        total_chunks = 0
        for file in os.listdir(KB_DIR):
            if not file.endswith(".md"):
                continue
                
            path = os.path.join(KB_DIR, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # chunk the doc
            chunks = chunk_text(content)
            print(f"  📄 {file}: {len(chunks)} chunks")
            
            # embed and store each chunk
            for i, chunk in enumerate(chunks):
                try:
                    embedding = get_embedding(chunk, model)
                    
                    conn.execute(
                        text("INSERT INTO kb_embeddings (doc_name, content, embedding) VALUES (:doc, :content, :emb)"),
                        {"doc": f"{file}_chunk{i+1}", "content": chunk, "emb": embedding}
                    )
                    total_chunks += 1
                except Exception as e:
                    print(f"Error embedding chunk {i+1}: {e}")
        
        print(f"\nSuccessfully loaded {total_chunks} chunks with LOCAL embeddings!")
        print("   (No API calls, runs on CPU, completely free!)")
        return total_chunks

if __name__ == "__main__":
    load_kb_documents()
