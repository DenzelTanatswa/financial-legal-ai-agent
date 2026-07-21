# Primary agent + which agents should collaborate per document type
_ROUTING = {
    "Bank Statement":  ("financial",  ["compliance"]),
    "Contract":        ("legal",       ["compliance", "financial"]),
    "Invoice":         ("invoice",     ["financial"]),
    "Tax Document":    ("tax",         ["compliance", "financial"]),
    "Compliance":      ("compliance",  ["legal"]),
}


def supervisor(state: dict) -> dict:
    doc = state.get("document_type", "")
    primary, collaborators = _ROUTING.get(doc, ("financial", ["compliance"]))
    state["selected_agent"]      = primary
    state["collaborating_agents"] = collaborators
    return state