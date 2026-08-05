from langchain_core.prompts import ChatPromptTemplate
from Agents._base import get_structured_llm, write_state
from core.models import InvoiceAnalysis

_PROMPT = ChatPromptTemplate.from_template("""
You are an Invoice Audit Specialist. Analyze the invoice below and return a structured analysis.

Context:
{context}

Question:
{question}

Extract vendor, invoice number, dates, all monetary amounts as numbers (subtotal, tax, total),
currency, line items, risks, and recommendations. Assign a confidence score between 0.0 and 1.0.
""")


def invoice_agent(state: dict) -> dict:
    chain = _PROMPT | get_structured_llm(InvoiceAnalysis)
    response: InvoiceAnalysis = chain.invoke({
        "context": state["context"],
        "question": state["question"],
    })
    response.document_type = state.get("document_type", "Invoice")
    return write_state(state, response)
