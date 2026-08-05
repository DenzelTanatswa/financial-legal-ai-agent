import json

from langchain_core.prompts import ChatPromptTemplate

from Agents._base import get_structured_llm
from core.models import ValidationReport
from services.logging_service import log_event

_PROMPT = ChatPromptTemplate.from_template("""
You are a response quality validator. Validate the structured analysis against
the retrieved document context. Return a structured validation report.

Check: missing fields; invalid structured output; unsupported claims; missing
document context; hallucination risk; invalid dates; inconsistent financial
amounts (subtotal, tax and total); and empty responses. Be conservative when
evidence is absent. Do not invent facts.

Document type: {document_type}
Analysis and retrieved context: {response}
""")


def validator_agent(state: dict) -> dict:
    structured = state.get("structured_response") or {}
    if not structured:
        state["validation_passed"] = False
        state["validation_error"] = "No structured agent response was produced."
        return state

    required = ("summary", "risks", "recommendations", "confidence")
    missing = [field for field in required if field not in structured or structured[field] in (None, "")]
    if missing:
        state["validation_passed"] = False
        state["validation_error"] = f"Missing required structured fields: {', '.join(missing)}"
        return state

    chain = _PROMPT | get_structured_llm(ValidationReport)
    report: ValidationReport = chain.invoke({
        "document_type": state.get("document_type", "Unknown"),
        "response": json.dumps({"analysis": structured, "retrieved_context": state.get("context", "")[:12000]}),
    })
    state["validation_passed"] = report.passed
    state["validation_report"] = report.model_dump()
    if not report.passed:
        state["confidence_score"] = round(state.get("confidence_score", 0.5) * report.overall_score, 4)
        log_event("validation_failed", document_type=state.get("document_type"), retry_count=state.get("retry_count", 0))
    return state


def validation_route(state: dict) -> str:
    """Retry once with the same typed schema; otherwise return a safe error."""
    if state.get("validation_passed"):
        return "final"
    if state.get("retry_count", 0) < 1:
        state["retry_count"] = state.get("retry_count", 0) + 1
        return "retry"
    state["response"] = "Analysis could not be validated reliably. Please review the source document or try again."
    state["structured_response"] = {"summary": state["response"], "risks": [], "recommendations": [], "confidence": 0.0, "safe_error": state.get("validation_error", "Validation failed")}
    return "final"
