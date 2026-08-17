from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .incident_api import router

app=FastAPI(title="DevOpsMentor AI",version="0.5.0")
app.include_router(router)
@app.get("/api/health")
def health(): return {"status":"ok","version":"0.5.0"}
app.mount("/",StaticFiles(directory=Path(__file__).resolve().parents[2]/"frontend",html=True),name="frontend")