from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.routes import ask, tools
from app.config import settings
import os

app = FastAPI(title="Deep Insights Copilot")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(ask.router)
app.include_router(tools.router)

@app.on_event("startup")
async def validate_required_keys():
    missing = []
    if not settings.DATABASE_URL.strip():
        missing.append("DATABASE_URL")
    if not settings.GROQ_API_KEY.strip():
        missing.append("GROQ_API_KEY")
    if not settings.JINA_API_KEY.strip():
        missing.append("JINA_API_KEY")
    if missing:
        raise RuntimeError(f"Missing required environment variable(s): {', '.join(missing)}")

@app.get("/")
def home():
    path = os.path.join("app", "static", "index.html")
    return FileResponse(path)
