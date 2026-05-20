# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = ""
    GROQ_API_KEY: str = ""  # basellm
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_MAX_TOKENS: int = 1024
    DEBUG: bool = False

    # Jina Embeddings API — must match pgvector column size in app/schema.sql (kb_embeddings.embedding)
    JINA_API_KEY: str = ""
    JINA_EMBEDDINGS_API_URL: str = "https://api.jina.ai/v1/embeddings"
    JINA_EMBEDDINGS_MODEL: str = "jina-embeddings-v3"
    JINA_EMBEDDING_DIMENSION: int = 1024  # default output size for jina-embeddings-v3

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

