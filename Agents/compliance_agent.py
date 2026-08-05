from langchain_core.prompts import ChatPromptTemplate
from Agents._base import get_structured_llm, write_state
from core.models import ComplianceAnalysis

_PROMPT = ChatPromptTemplate.from_template("""
You are a Compliance Officer. Assess the document for regulatory compliance and return a structured analysis.

Context:
{context}

Question:
{question}

Determine compliance status (COMPLIANT, NON-COMPLIANT, PARTIAL, or UNKNOWN), list any violated
regulations, required actions, risks, and recommendations. Assign a confidence score between 0.0 and 1.0.
""")


def compliance_agent(state: dict) -> dict:
    chain = _PROMPT | get_structured_llm(ComplianceAnalysis)
    response: ComplianceAnalysis = chain.invoke({
        "context": state["context"],
        "question": state["question"],
    })
    response.document_type = state.get("document_type", "Unknown")
    return write_state(state, response)
