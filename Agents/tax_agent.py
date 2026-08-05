from langchain_core.prompts import ChatPromptTemplate
from Agents._base import get_structured_llm, write_state
from core.models import TaxAnalysis

_PROMPT = ChatPromptTemplate.from_template("""
You are a Tax Compliance Expert. Analyze the tax document below and return a structured analysis.

Context:
{context}

Question:
{question}

Extract tax year, all monetary figures as numbers (income, deductions, taxable income, liability),
effective tax rate as a decimal, highlights, risks, and recommendations.
Assign a confidence score between 0.0 and 1.0.
""")


def tax_agent(state: dict) -> dict:
    chain = _PROMPT | get_structured_llm(TaxAnalysis)
    response: TaxAnalysis = chain.invoke({
        "context": state["context"],
        "question": state["question"],
    })
    response.document_type = state.get("document_type", "Tax Document")
    return write_state(state, response)
