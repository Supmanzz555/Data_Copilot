from fastapi import FastAPI
from fastapi.responses import FileResponse
from app.routes import ask, tools
import os

app = FastAPI(title="Deep Insights Copilot")

app.include_router(ask.router)
app.include_router(tools.router)

@app.get("/")
def home():
    path = os.path.join("app", "static", "index.html")
    return FileResponse(path)
