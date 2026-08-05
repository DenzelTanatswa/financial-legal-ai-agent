from __future__ import annotations
from typing import Type, TypeVar
from pydantic import BaseModel
from Agents.llm import llm

T = TypeVar("T", bound=BaseModel)


def get_structured_llm(schema: Type[T]):
    """Bind the LLM to a Pydantic schema using native structured output."""
    return llm.with_structured_output(schema)


def write_state(state: dict, response: BaseModel) -> dict:
    """Write a structured Pydantic response into the LangGraph state dict."""
    data = response.model_dump()
    state["structured_response"] = data
    state["response"] = data.get("summary", "")
    state["confidence_score"] = data.get("confidence", data.get("confidence_score", 0.0))
    state["confidence_rationale"] = data.get("confidence_rationale", "")
    state["reasoning_steps"] = [
        s.model_dump() if hasattr(s, "model_dump") else s
        for s in (response.reasoning_steps if hasattr(response, "reasoning_steps") else [])
    ]
    existing = state.get("agent_responses") or []
    existing.append(data)
    state["agent_responses"] = existing
    return state
