from __future__ import annotations
import statistics
from core.models import CollaborationResult, RiskItem


def _merge_risks(responses: list[dict]) -> list[RiskItem]:
    seen: set[tuple] = set()
    merged: list[RiskItem] = []
    for r in responses:
        for risk in r.get("risks", []):
            if not isinstance(risk, dict):
                continue
            key = (risk.get("severity", ""), risk.get("description", "")[:60])
            if key not in seen:
                seen.add(key)
                merged.append(RiskItem(**risk))
    return merged


def _merge_list(responses: list[dict], *fields: str) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []
    for r in responses:
        for field in fields:
            for item in r.get(field, []):
                if isinstance(item, str) and item not in seen:
                    seen.add(item)
                    merged.append(item)
    return merged


def collaborator_agent(state: dict) -> dict:
    all_responses: list[dict] = state.get("agent_responses") or []
    if not all_responses:
        return state

    primary_response = state.get("structured_response") or all_responses[0]
    merged_risks = _merge_risks(all_responses)
    merged_recs = _merge_list(all_responses, "recommendations")
    # Collect highlights from whichever field each agent populates
    merged_highlights = _merge_list(all_responses, "financial_highlights", "required_actions")

    scores = [
        r.get("confidence", r.get("confidence_score", 0.5))
        for r in all_responses if r
    ]
    overall_confidence = round(statistics.mean(scores), 4) if scores else 0.5

    # Per-agent summary breakdown for UI display
    agent_breakdown = [
        {
            "agent_name":  r.get("agent_name", "Agent"),
            "summary":     r.get("summary", ""),
            "confidence":  r.get("confidence", r.get("confidence_score", 0.0)),
            "risk_count":  len(r.get("risks", [])),
        }
        for r in all_responses
    ]

    merged_summary = "\n\n".join(
        f"**{r.get('agent_name', 'Agent')}**: {r.get('summary', '')}"
        for r in all_responses if r.get("summary")
    )

    result = CollaborationResult(
        primary_agent=primary_response.get("agent_name", state.get("selected_agent", "")),
        collaborating_agents=state.get("collaborating_agents", []),
        merged_summary=merged_summary,
        merged_risks=merged_risks,
        merged_recommendations=merged_recs,
        overall_confidence=overall_confidence,
        agent_responses=all_responses,
    )

    state["structured_response"] = {
        **(state.get("structured_response") or {}),
        "collaboration": {
            **result.model_dump(),
            "agent_breakdown": agent_breakdown,
        },
        "financial_highlights": merged_highlights,
        "risks":           [r.model_dump() for r in merged_risks],
        "recommendations": merged_recs,
    }
    state["response"] = merged_summary
    state["confidence_score"] = overall_confidence
    state["agent_responses"] = all_responses
    return state
