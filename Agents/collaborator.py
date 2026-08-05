from __future__ import annotations
import statistics
from core.models import CollaborationResult, RiskItem


def _agent_map():
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


def _merge_risks(responses: list[dict]) -> list[RiskItem]:
    seen, merged = set(), []
    for r in responses:
        for risk in r.get("risks", []):
            if not isinstance(risk, dict):
                continue
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
    if not state.get("agent_responses"):
        return state
    collab_keys = state.get("collaborating_agents", [])
    all_responses = state["agent_responses"]
    primary_response = state.get("structured_response") or all_responses[0]

    merged_risks = _merge_risks(all_responses)
    merged_recs = _merge_list(all_responses, "recommendations")
    merged_findings = _merge_list(all_responses, "financial_highlights") or _merge_list(all_responses, "important_clauses")
    scores = [r.get("confidence", r.get("confidence_score", 0.5)) for r in all_responses if r]
    overall_confidence = round(statistics.mean(scores), 4) if scores else 0.5
    merged_summary = "\n\n".join(
        f"{r.get('agent_name', 'Agent')}: {r.get('summary', '')}"
        for r in all_responses if r.get("summary")
    )

    result = CollaborationResult(
        primary_agent=primary_response.get("agent_name", state.get("selected_agent", "")),
        collaborating_agents=collab_keys,
        merged_summary=merged_summary,
        merged_risks=merged_risks,
        merged_recommendations=merged_recs,
        overall_confidence=overall_confidence,
        agent_responses=all_responses,
    )

    state["structured_response"] = {
        **(state.get("structured_response") or {}),
        "collaboration": result.model_dump(),
        "financial_highlights": merged_findings,
        "risks": [r.model_dump() for r in merged_risks],
        "recommendations": merged_recs,
    }
    state["response"] = merged_summary
    state["confidence_score"] = overall_confidence
    state["agent_responses"] = all_responses
    return state
