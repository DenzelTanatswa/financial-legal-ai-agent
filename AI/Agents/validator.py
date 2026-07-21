import json
from langchain_core.prompts import ChatPromptTemplate
from AI.llm import llm
from AI.prompts import VALIDATOR_PROMPT
from AI.schemas import ValidationReport, ValidationCheck
from AI.Agents._base import parse_llm_json


def validator_agent(state: dict) -> dict:
    structured = state.get("structured_response") or {}
    if not structured:
        return state

    chain = ChatPromptTemplate.from_template(VALIDATOR_PROMPT) | llm
    raw = chain.invoke({
        "document_type": state.get("document_type", "Unknown"),
        "response": json.dumps(structured, indent=2),
    }).content
    data = parse_llm_json(raw)

    checks = [
        ValidationCheck(**c)
        for c in data.get("checks", [])
        if isinstance(c, dict)
    ]
    report = ValidationReport(
        passed=bool(data.get("passed", False)),
        overall_score=float(data.get("overall_score", 0.0)),
        checks=checks,
    )

    state["validation_passed"] = report.passed
    state["validation_report"] = report.model_dump()

    # Penalise confidence if validation failed
    if not report.passed:
        state["confidence_score"] = round(
            state.get("confidence_score", 0.5) * report.overall_score, 4
        )

    return state
