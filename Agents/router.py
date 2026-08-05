from Agents.financial_agent import financial_agent
from Agents.legal_agent import legal_agent
from Agents.invoice_agent import invoice_agent
from Agents.tax_agent import tax_agent
from Agents.compliance_agent import compliance_agent


def route(state: dict) -> dict:
    agent = state["selected_agent"]
    dispatch = {
        "financial":  financial_agent,
        "legal":      legal_agent,
        "invoice":    invoice_agent,
        "tax":        tax_agent,
        "compliance": compliance_agent,
    }
    return dispatch.get(agent, financial_agent)(state)
