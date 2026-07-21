"""Shared helper used by every agent — parse LLM JSON, fallback on error, write state."""
from __future__ import annotations
import json
import re
from typing import Any, Dict, Type
from AI.schemas import BaseAgentResponse, ReasoningStep, RiskItem


def _strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` wrappers the LLM sometimes adds."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def parse_llm_json(raw: str) -> Dict[str, Any]:
    try:
        return json.loads(_strip_markdown_fences(raw))
    except json.JSONDecodeError:
        return {
            "summary": raw,
            "key_findings": [],
            "risks": [],
            "recommendations": [],
            "confidence_score": 0.3,
            "confidence_rationale": "Could not parse structured output — raw text returned.",
            "reasoning_steps": [],
        }


def build_risks(data: Dict[str, Any]):
    return [RiskItem(**r) for r in data.get("risks", []) if isinstance(r, dict)]


def build_steps(data: Dict[str, Any]):
    return [ReasoningStep(**s) for s in data.get("reasoning_steps", []) if isinstance(s, dict)]


def write_state(state: dict, response: BaseAgentResponse) -> dict:
    state["structured_response"]  = response.model_dump()
    state["response"]             = response.summary
    state["confidence_score"]     = response.confidence_score
    state["confidence_rationale"] = response.confidence_rationale
    state["reasoning_steps"]      = [s.model_dump() for s in response.reasoning_steps]
    existing = state.get("agent_responses") or []
    existing.append(response.model_dump())
    state["agent_responses"] = existing
    return state
