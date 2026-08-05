from langchain_core.prompts import ChatPromptTemplate
from Agents._base import get_structured_llm, write_state
from core.models import LegalAnalysis

_PROMPT = ChatPromptTemplate.from_template("""
You are a senior Legal Analyst. Review the contract document below and return a structured analysis.

Context:
{context}

Question:
{question}

Identify all parties with their roles, governing law, effective and termination dates,
important clauses, risks, and recommendations. Assign a confidence score between 0.0 and 1.0.
""")


def legal_agent(state: dict) -> dict:
    chain = _PROMPT | get_structured_llm(LegalAnalysis)
    response: LegalAnalysis = chain.invoke({
        "context": state["context"],
        "question": state["question"],
    })
    response.document_type = state.get("document_type", "Contract")
    return write_state(state, response)
