from __future__ import annotations
import statistics
from AI.schemas import CollaborationResult, RiskItem, BaseAgentResponse


# Map agent keys to their callables — imported lazily to avoid circular imports
def _agent_map():
    from AI.Agents.financial_agent import financial_agent
    from AI.Agents.legal_agent import legal_agent
    from AI.Agents.invoice_agent import invoice_agent
    from AI.Agents.tax_agent import tax_agent
    from AI.Agents.compliance_agent import compliance_agent
    return {
        "financial": financial_agent,
        "legal": legal_agent,
        "invoice": invoice_agent,
        "tax": tax_agent,
        "compliance": compliance_agent,
    }


def _merge_risks(responses: list[dict]) -> list[RiskItem]:
    seen, merged = set(), []
    for r in responses:
        for risk in r.get("risks", []):
            key = (risk.get("severity", ""), risk.get("description", "")[:60])
            if key not in seen:
                seen.add(key)
                merged.append(RiskItem(**risk))
    return merged


def _merge_list(responses: list[dict], field: str) -> list[str]:
    seen, merged = set(), []
    for r in responses:
        for item in r.get(field, []):
            if item not in seen:
                seen.add(item)
                merged.append(item)
    return merged


def collaborator_agent(state: dict) -> dict:
    collab_keys = state.get("collaborating_agents", [])
    if not collab_keys:
        return state

    agents = _agent_map()
    primary_response = (state.get("agent_responses") or [{}])[-1]
    all_responses = [primary_response]

    for key in collab_keys:
        fn = agents.get(key)
        if fn is None:
            continue
        # Run each secondary agent on a clean copy of state
        sub_state = {**state, "agent_responses": []}
        sub_state = fn(sub_state)
        secondary = (sub_state.get("agent_responses") or [{}])[-1]
        all_responses.append(secondary)

    merged_risks = _merge_risks(all_responses)
    merged_recs  = _merge_list(all_responses, "recommendations")
    merged_findings = _merge_list(all_responses, "key_findings")

    scores = [r.get("confidence_score", 0.5) for r in all_responses if r.get("confidence_score") is not None]
    overall_confidence = round(statistics.mean(scores), 4) if scores else 0.5

    summaries = [r.get("summary", "") for r in all_responses if r.get("summary")]
    merged_summary = "\n\n---\n\n".join(
        f"**{r.get('agent_name', 'Agent')}:** {r.get('summary', '')}"
        for r in all_responses if r.get("summary")
    )

    result = CollaborationResult(
        primary_agent=primary_response.get("agent_name", state.get("selected_agent", "")),
        collaborating_agents=collab_keys,
        merged_summary=merged_summary,
        merged_risks=merged_risks,
        merged_recommendations=merged_recs,
        overall_confidence=overall_confidence,
        agent_responses=[BaseAgentResponse(**r) for r in all_responses if r],
    )

    state["structured_response"] = {
        **(state.get("structured_response") or {}),
        "collaboration": result.model_dump(),
        "key_findings": merged_findings,
        "risks": [r.model_dump() for r in merged_risks],
        "recommendations": merged_recs,
    }
    state["response"] = merged_summary
    state["confidence_score"] = overall_confidence
    state["agent_responses"] = [r.model_dump() for r in result.agent_responses]

    return state
