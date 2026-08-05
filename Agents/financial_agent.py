from langchain_core.prompts import ChatPromptTemplate
from Agents._base import get_structured_llm, write_state
from core.models import FinancialAnalysis

_PROMPT = ChatPromptTemplate.from_template("""
You are a senior Financial Analyst. Analyze the financial document below and return a structured analysis.

Context:
{context}

Question:
{question}

Extract all financial figures as numbers (not strings). Populate `income`, `expenses`, and
`cashflow` with document totals; use null when a value is not stated. Identify highlights,
risks, and recommendations. Assign a confidence score between 0.0 and 1.0.
""")


def financial_agent(state: dict) -> dict:
    chain = _PROMPT | get_structured_llm(FinancialAnalysis)
    response: FinancialAnalysis = chain.invoke({
        "context": state["context"],
        "question": state["question"],
    })
    response.document_type = state.get("document_type", "Bank Statement")
    return write_state(state, response)
