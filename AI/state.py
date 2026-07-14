from typing import TypedDict


class AgentState(TypedDict):
    question: str
    context: str
    document_type: str
    selected_agent: str
    response: str