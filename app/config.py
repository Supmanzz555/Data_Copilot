# app/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://admin:admin@db:5432/deep_insights"
    GROQ_API_KEY: str = ""  # basellm
    

    class Config:
        env_file = ".env"

settings = Settings()

