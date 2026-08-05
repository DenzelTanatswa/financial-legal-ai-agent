"""Parallel specialist execution for independent document reviews."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from time import perf_counter

from Agents.collaborator import _agent_map
from services.logging_service import log_event


def run_required_agents(state: dict) -> dict:
    agents = _agent_map()
    required = state.get("required_agents") or [state.get("selected_agent", "financial")]
    responses, runs = [], []

    def run_one(agent_key: str):
        started = perf_counter()
        sub_state = {**state, "agent_responses": [], "structured_response": None}
        result = agents[agent_key](sub_state)
        response = (result.get("agent_responses") or [{}])[-1]
        elapsed = round(perf_counter() - started, 3)
        return agent_key, response, elapsed

    with ThreadPoolExecutor(max_workers=len(required)) as executor:
        futures = [executor.submit(run_one, key) for key in required if key in agents]
        for future in as_completed(futures):
            agent_key, response, elapsed = future.result()
            responses.append(response)
            runs.append({"agent": agent_key, "execution_seconds": elapsed, "status": "completed"})
            log_event("agent_run", agent=agent_key, execution_seconds=elapsed)

    # Preserve deterministic primary-first ordering for aggregation and display.
    order = {key: index for index, key in enumerate(required)}
    responses.sort(key=lambda response: order.get(response.get("agent_name", "").split()[0].lower(), 99))
    state["agent_responses"] = responses
    state["agent_runs"] = runs
    primary = next((r for r in responses if r.get("agent_name") == {"financial":"Financial Analyst", "legal":"Contract Reviewer", "invoice":"Invoice Analyzer", "tax":"Tax Assistant", "compliance":"Compliance Officer"}.get(state.get("selected_agent"))), responses[0] if responses else {})
    state["structured_response"] = primary
    state["response"] = primary.get("summary", "")
    state["confidence_score"] = primary.get("confidence", 0.0)
    return state
