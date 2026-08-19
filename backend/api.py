from fastapi import APIRouter
from pydantic import BaseModel

from tools.clause_classifier import classifier

router=APIRouter()

class ClaudeRequest(BaseModel):
    text: str

@router.post("/predict")
def predict_clause(request: ClaudeRequest):
    result = classifier.predict(request.text)
    return result