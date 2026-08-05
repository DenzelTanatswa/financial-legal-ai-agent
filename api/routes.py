"""Typed REST interface for structured analysis results."""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from services.analysis_service import analyze_document

router = APIRouter(prefix="/api/v1", tags=["analysis"])


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1)
    document_type: str = Field(min_length=1)
    question: str = "Summarize this document."


@router.post("/analyze")
def analyze(payload: AnalyzeRequest) -> dict:
    """Return JSON-native, schema-backed data rather than markdown text."""
    result = analyze_document(payload.text, payload.document_type, payload.question)
    return result["analysis_response"] or {"analysis": result["structured"]}
