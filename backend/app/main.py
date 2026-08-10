from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .incident_api import router as incident_router

app = FastAPI(title="DevOpsMentor AI", version="0.4.0")
app.include_router(incident_router)

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.4.0"}

frontend_dir = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
