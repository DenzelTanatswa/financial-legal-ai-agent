from repositories.vector_store_repo import build_vector_store, retrieve_context, retrieve_sources
from Agents.graph import graph
from core.models import (
    AnalysisResponse,
    ComplianceAnalysis,
    FinancialAnalysis,
    InvoiceAnalysis,
    LegalAnalysis,
    TaxAnalysis,
    SystemConfidence,
    ValidationReport,
)


_ANALYSIS_MODEL_BY_AGENT = {
    "Financial Analyst": FinancialAnalysis,
    "Contract Reviewer": LegalAnalysis,
    "Invoice Analyzer": InvoiceAnalysis,
    "Tax Assistant": TaxAnalysis,
    "Compliance Officer": ComplianceAnalysis,
}


def analyze_document(text: str, document_type: str, question: str, conversation_history: list[dict] | None = None) -> dict:
    vector_store = build_vector_store(text)
    context = retrieve_context(vector_store, question)
    source_references = retrieve_sources(vector_store, question)
    history = conversation_history or []
    history_text = "\n".join(
        f"{message.get('role', 'user').title()}: {message.get('content', '')}"
        for message in history[-8:]
    )
    question_with_memory = (
        f"Conversation context for the same document:\n{history_text}\n\nCurrent question: {question}"
        if history_text else question
    )

    state = {
        "question": question_with_memory,
        "conversation_history": conversation_history or [],
        "context": context,
        "document_type": document_type,
        "extracted_text": text,
        "selected_agent": "",
        "required_agents": [],
        "response": "",
        "structured_response": None,
        "confidence_score": 0.0,
        "confidence_rationale": "",
        "reasoning_steps": [],
        "agent_responses": [],
        "validation_passed": True,
        "validation_report": None,
        "collaborating_agents": [],
        "retry_count": 0,
        "validation_error": None,
    }

    result = graph.invoke(state)

    structured = result.get("structured_response") or {}
    analysis_model = _ANALYSIS_MODEL_BY_AGENT.get(
        structured.get("agent_name") or result.get("selected_agent")
    )
    analysis = analysis_model.model_validate(structured) if analysis_model else None
    validation = (
        ValidationReport.model_validate(result["validation_report"])
        if result.get("validation_report") else None
    )

    response = AnalysisResponse(
        document_type=document_type,
        selected_agent=result.get("selected_agent", structured.get("agent_name", "")),
        analysis=analysis,
        validation=validation,
        collaborating_agents=result.get("collaborating_agents", []),
    ) if analysis else None
    analysis_confidence = SystemConfidence.from_score(
        result.get("confidence_score", 0.0),
        result.get("confidence_rationale", "") or "Derived from the model output and validation checks.",
    )

    return {
        "summary":               result.get("response", ""),
        "structured":            analysis.model_dump(mode="json") if analysis else structured,
        "analysis_response":     response.to_api_payload() if response else None,
        "confidence_score":      result.get("confidence_score", 0.0),
        "confidence_rationale":  result.get("confidence_rationale", ""),
        "analysis_confidence":   analysis_confidence.model_dump(mode="json"),
        "reasoning_steps":       result.get("reasoning_steps", []),
        "validation_report":     result.get("validation_report"),
        "validation_passed":     result.get("validation_passed", True),
        "collaborating_agents":  result.get("collaborating_agents", []),
        "agent_responses":       result.get("agent_responses", []),
        "agent_runs":            result.get("agent_runs", []),
        "source_references":     source_references,
    }
