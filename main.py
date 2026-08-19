from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.api import router as api_router

app = FastAPI(
    title="LegalLens API",
    description="AI-powered legal contract analysis",
    version="0.1.0",
)

app.include_router(api_router)

@app.get("/health")
def health():
    return {"status": "healthy"}

dist = Path("frontend/dist")
if dist.exists():
    app.mount("/", StaticFiles(directory=str(dist), html=True), name="frontend")