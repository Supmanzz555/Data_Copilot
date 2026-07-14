from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes import ask, tools
from app.metrics import router as metrics_router
from app.config import settings
import os

app = FastAPI(title="Deep Insights Copilot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
app.include_router(metrics_router)
app.include_router(ask.router)
app.include_router(tools.router)


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})

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
