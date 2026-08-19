import shutil
import tempfile
from pathlib import Path
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel
from agent.answer_engine import engine
from rag.contract.load import _get_classifier
from rag.contract.retrieval import delete_session

router = APIRouter()

class ClauseRequest(BaseModel):
    text: str

@router.post("/predict")
def predict_clause(request: ClauseRequest):
    """Classify a single clause text with BERT."""
    return _get_classifier().classify(request.text)

@router.post("/upload")
async def upload_contract(file: UploadFile = File(...)):
    """
    Upload a contract (PDF, DOCX, TXT, PNG, JPG).
    Returns session_id to use in /chat.
    """
    allowed = {".pdf", ".docx", ".doc", ".txt", ".png", ".jpg", ".jpeg"}
    suffix = Path(file.filename).suffix.lower()
    if suffix not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {', '.join(allowed)}"
        )
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    try:
        result = engine.ingest(tmp_path, original_filename=file.filename)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        Path(tmp_path).unlink(missing_ok=True)
    return {
        "session_id": result["session_id"],
        "source": result["source"],
        "clause_count": result["clause_count"],
        "clause_summary": result["clause_summary"],
    }

class ChatRequest(BaseModel):
    session_id: str
    message: str

@router.post("/chat")
def chat(request: ChatRequest):
    """Answer a question using Contract RAG + Legal KB RAG + Groq."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    try:
        return engine.chat(session_id=request.session_id, question=request.message)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.delete("/session/{session_id}")
def close_session(session_id: str):
    """Delete in-memory Chroma collection for a session."""
    deleted = delete_session(session_id)
    return {"deleted": deleted, "session_id": session_id}