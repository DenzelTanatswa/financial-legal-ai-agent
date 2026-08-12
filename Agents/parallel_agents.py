"""Parallel specialist execution for independent document reviews."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import perf_counter

from services.logging_service import log_event

# Canonical mapping: routing key → display agent_name (must match model defaults)
_KEY_TO_NAME: dict[str, str] = {
    "financial":  "Financial Analyst",
    "legal":      "Contract Reviewer",
    "invoice":    "Invoice Analyzer",
    "tax":        "Tax Assistant",
    "compliance": "Compliance Officer",
}


def _agent_map() -> dict:
    from Agents.financial_agent import financial_agent
    from Agents.legal_agent import legal_agent
    from Agents.invoice_agent import invoice_agent
    from Agents.tax_agent import tax_agent
    from Agents.compliance_agent import compliance_agent
    return {
        "financial":  financial_agent,
        "legal":      legal_agent,
        "invoice":    invoice_agent,
        "tax":        tax_agent,
        "compliance": compliance_agent,
    }


def run_required_agents(state: dict) -> dict:
    agents = _agent_map()
    required: list[str] = state.get("required_agents") or [state.get("selected_agent", "financial")]
    # Only dispatch agents that exist in the registry
    required = [k for k in required if k in agents]

    responses: list[dict] = []
    runs: list[dict] = []

    def _run_one(agent_key: str) -> tuple[str, dict, float]:
        started = perf_counter()
        # Each agent gets an isolated copy of state so parallel writes don't collide
        sub_state = {**state, "agent_responses": [], "structured_response": None}
        result = agents[agent_key](sub_state)
        response = (result.get("agent_responses") or [{}])[-1]
        return agent_key, response, round(perf_counter() - started, 3)

    with ThreadPoolExecutor(max_workers=len(required)) as executor:
        futures = {executor.submit(_run_one, key): key for key in required}
        for future in as_completed(futures):
            agent_key, response, elapsed = future.result()
            responses.append(response)
            runs.append({
                "agent":              agent_key,
                "agent_name":         _KEY_TO_NAME.get(agent_key, agent_key),
                "execution_seconds":  elapsed,
                "status":             "completed",
            })
            log_event("agent_run", agent=agent_key, execution_seconds=elapsed)

    # Restore deterministic primary-first ordering using the required list index
    order = {key: idx for idx, key in enumerate(required)}
    # Map each response back to its routing key via the canonical name map
    _name_to_key = {v: k for k, v in _KEY_TO_NAME.items()}
    responses.sort(
        key=lambda r: order.get(_name_to_key.get(r.get("agent_name", ""), ""), 99)
    )
    runs.sort(key=lambda r: order.get(r["agent"], 99))

    primary_key = state.get("selected_agent", required[0] if required else "financial")
    primary_name = _KEY_TO_NAME.get(primary_key, "")
    primary = next(
        (r for r in responses if r.get("agent_name") == primary_name),
        responses[0] if responses else {},
    )

    state["agent_responses"] = responses
    state["agent_runs"] = runs
    state["structured_response"] = primary
    state["response"] = primary.get("summary", "")
    state["confidence_score"] = primary.get("confidence", 0.0)
    return state
