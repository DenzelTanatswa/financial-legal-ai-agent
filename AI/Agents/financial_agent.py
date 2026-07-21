from langchain_core.prompts import ChatPromptTemplate
from AI.llm import llm
from AI.prompts import FINANCIAL_PROMPT
from AI.schemas import FinancialAgentResponse, RiskItem, ReasoningStep
from AI.Agents._base import parse_llm_json, build_risks, build_steps, write_state


def financial_agent(state: dict) -> dict:
    chain = ChatPromptTemplate.from_template(FINANCIAL_PROMPT) | llm
    raw   = chain.invoke({"context": state["context"], "question": state["question"]}).content
    data  = parse_llm_json(raw)

    response = FinancialAgentResponse(
        document_type    = state.get("document_type", "Bank Statement"),
        summary          = data.get("summary", ""),
        key_findings     = data.get("key_findings", []),
        key_figures      = data.get("key_figures", []),
        total_amount     = data.get("total_amount"),
        period_covered   = data.get("period_covered"),
        risks            = build_risks(data),
        recommendations  = data.get("recommendations", []),
        confidence_score = float(data.get("confidence_score", 0.5)),
        confidence_rationale = data.get("confidence_rationale", ""),
        reasoning_steps  = build_steps(data),
    )
    return write_state(state, response)
