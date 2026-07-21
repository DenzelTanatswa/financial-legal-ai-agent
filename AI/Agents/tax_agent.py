from langchain_core.prompts import ChatPromptTemplate
from AI.llm import llm
from AI.prompts import TAX_PROMPT
from AI.schemas import TaxAgentResponse
from AI.Agents._base import parse_llm_json, build_risks, build_steps, write_state


def tax_agent(state: dict) -> dict:
    chain = ChatPromptTemplate.from_template(TAX_PROMPT) | llm
    raw   = chain.invoke({"context": state["context"], "question": state["question"]}).content
    data  = parse_llm_json(raw)

    response = TaxAgentResponse(
        document_type        = state.get("document_type", "Tax Document"),
        summary              = data.get("summary", ""),
        key_findings         = data.get("key_findings", []),
        tax_year             = data.get("tax_year"),
        total_income         = data.get("total_income"),
        total_deductions     = data.get("total_deductions"),
        tax_liability        = data.get("tax_liability"),
        risks                = build_risks(data),
        recommendations      = data.get("recommendations", []),
        confidence_score     = float(data.get("confidence_score", 0.5)),
        confidence_rationale = data.get("confidence_rationale", ""),
        reasoning_steps      = build_steps(data),
    )
    return write_state(state, response)
