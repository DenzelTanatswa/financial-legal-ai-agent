from AI.graph import graph
from AI.vector_store import build_vector_store
from AI.rag import retrieve_context


def analyze_document(text: str, document_type: str, question: str) -> dict:
    vector_store = build_vector_store(text)
    context = retrieve_context(vector_store, question)

    state = {
        "question": question,
        "context": context,
        "document_type": document_type,
        "selected_agent": "",
        "response": "",
        "structured_response": None,
        "confidence_score": 0.0,
        "confidence_rationale": "",
        "reasoning_steps": [],
        "agent_responses": [],
        "validation_passed": True,
        "validation_report": None,
        "collaborating_agents": [],
    }

    result = graph.invoke(state)

    return {
        "summary": result.get("response", ""),
        "structured": result.get("structured_response") or {},
        "confidence_score": result.get("confidence_score", 0.0),
        "confidence_rationale": result.get("confidence_rationale", ""),
        "reasoning_steps": result.get("reasoning_steps", []),
        "validation_report": result.get("validation_report"),
        "validation_passed": result.get("validation_passed", True),
        "collaborating_agents": result.get("collaborating_agents", []),
        "agent_responses": result.get("agent_responses", []),
    }