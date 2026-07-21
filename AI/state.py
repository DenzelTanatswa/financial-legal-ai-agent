from __future__ import annotations
from typing import Any, Dict, List, Optional, TypedDict


class AgentState(TypedDict):
    # Input
    question: str
    context: str
    document_type: str
    extracted_text: str

    # Routing
    selected_agent: str
    collaborating_agents: List[str]

    # Outputs
    response: str
    structured_response: Optional[Dict[str, Any]]
    confidence_score: float
    confidence_rationale: str

    # Collaboration
    agent_responses: List[Dict[str, Any]]

    # Validation
    validation_passed: bool
    validation_report: Optional[Dict[str, Any]]

    # Explainability
    reasoning_steps: List[Dict[str, Any]]
