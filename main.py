from fastapi import FastAPI

from backend.api import router as api_router


app = FastAPI(
    title="LegalLens API",
    description="AI-powered legal contract analysis API",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "LegalLens API is running",
        "status": "ok"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


app.include_router(api_router)