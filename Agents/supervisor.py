_ROUTING = {
    "Bank Statement": ("financial", ["financial", "compliance"]),
    "Contract":       ("legal", ["financial", "legal", "compliance"]),
    "Invoice":        ("invoice", ["invoice", "financial", "compliance"]),
    "Tax Document":   ("tax", ["tax", "financial", "compliance"]),
    "Compliance":     ("compliance", ["legal", "compliance"]),
}


def supervisor(state: dict) -> dict:
    doc = state.get("document_type", "")
    primary, required_agents = _ROUTING.get(doc, ("financial", ["financial", "compliance"]))
    state["selected_agent"] = primary
    state["required_agents"] = required_agents
    state["collaborating_agents"] = [agent for agent in required_agents if agent != primary]
    return state
