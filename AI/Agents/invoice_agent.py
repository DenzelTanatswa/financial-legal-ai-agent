from langchain_core.prompts import ChatPromptTemplate
from AI.llm import llm
from AI.prompts import INVOICE_PROMPT
from AI.schemas import InvoiceAgentResponse
from AI.Agents._base import parse_llm_json, build_risks, build_steps, write_state


def invoice_agent(state: dict) -> dict:
    chain = ChatPromptTemplate.from_template(INVOICE_PROMPT) | llm
    raw   = chain.invoke({"context": state["context"], "question": state["question"]}).content
    data  = parse_llm_json(raw)

    response = InvoiceAgentResponse(
        document_type        = state.get("document_type", "Invoice"),
        summary              = data.get("summary", ""),
        key_findings         = data.get("key_findings", []),
        vendor               = data.get("vendor"),
        invoice_number       = data.get("invoice_number"),
        amount_due           = data.get("amount_due"),
        due_date             = data.get("due_date"),
        risks                = build_risks(data),
        recommendations      = data.get("recommendations", []),
        confidence_score     = float(data.get("confidence_score", 0.5)),
        confidence_rationale = data.get("confidence_rationale", ""),
        reasoning_steps      = build_steps(data),
    )
    return write_state(state, response)
