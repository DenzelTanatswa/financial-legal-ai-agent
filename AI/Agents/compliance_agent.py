from langchain_core.prompts import ChatPromptTemplate
from AI.llm import llm
from AI.prompts import COMPLIANCE_PROMPT
from AI.schemas import ComplianceAgentResponse
from AI.Agents._base import parse_llm_json, build_risks, build_steps, write_state


def compliance_agent(state: dict) -> dict:
    chain = ChatPromptTemplate.from_template(COMPLIANCE_PROMPT) | llm
    raw   = chain.invoke({"context": state["context"], "question": state["question"]}).content
    data  = parse_llm_json(raw)

    response = ComplianceAgentResponse(
        document_type        = state.get("document_type", "Unknown"),
        summary              = data.get("summary", ""),
        key_findings         = data.get("key_findings", []),
        compliance_status    = data.get("compliance_status", "UNKNOWN"),
        violated_regulations = data.get("violated_regulations", []),
        required_actions     = data.get("required_actions", []),
        risks                = build_risks(data),
        recommendations      = data.get("recommendations", []),
        confidence_score     = float(data.get("confidence_score", 0.5)),
        confidence_rationale = data.get("confidence_rationale", ""),
        reasoning_steps      = build_steps(data),
    )
    return write_state(state, response)
