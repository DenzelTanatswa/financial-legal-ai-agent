from langchain_core.prompts import ChatPromptTemplate
from AI.llm import llm
from AI.prompts import LEGAL_PROMPT
from AI.schemas import LegalAgentResponse
from AI.Agents._base import parse_llm_json, build_risks, build_steps, write_state


def legal_agent(state: dict) -> dict:
    chain = ChatPromptTemplate.from_template(LEGAL_PROMPT) | llm
    raw   = chain.invoke({"context": state["context"], "question": state["question"]}).content
    data  = parse_llm_json(raw)

    response = LegalAgentResponse(
        document_type        = state.get("document_type", "Contract"),
        summary              = data.get("summary", ""),
        key_findings         = data.get("key_findings", []),
        parties_involved     = data.get("parties_involved", []),
        governing_law        = data.get("governing_law"),
        effective_date       = data.get("effective_date"),
        termination_clauses  = data.get("termination_clauses", []),
        risks                = build_risks(data),
        recommendations      = data.get("recommendations", []),
        confidence_score     = float(data.get("confidence_score", 0.5)),
        confidence_rationale = data.get("confidence_rationale", ""),
        reasoning_steps      = build_steps(data),
    )
    return write_state(state, response)
