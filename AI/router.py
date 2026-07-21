from AI.Agents.financial_agent import financial_agent
from AI.Agents.legal_agent import legal_agent
from AI.Agents.invoice_agent import invoice_agent


def route(state):

    agent = state["selected_agent"]

    if agent == "financial":
        return financial_agent(state)

    if agent == "legal":
        return legal_agent(state)

    if agent == "invoice":
        return invoice_agent(state)

    return financial_agent(state)