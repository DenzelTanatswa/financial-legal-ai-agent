import re

DOCUMENT_PATTERNS = {
    "Bank Statement": [
        r"available balance", r"transaction", r"account number",
        r"withdrawal", r"deposit", r"bank statement", r"opening balance",
    ],
    "Invoice": [
        r"invoice", r"invoice number", r"due date",
        r"vat", r"subtotal", r"total amount",
    ],
    "Contract": [
        r"agreement", r"party", r"contract",
        r"termination", r"governing law", r"effective date",
    ],
    "Tax Document": [
        r"tax", r"income", r"deduction", r"taxpayer", r"return",
    ],
}


def classify_document(text):
    text   = text.lower()
    scores = {
        doc_type: sum(1 for p in patterns if re.search(p, text))
        for doc_type, patterns in DOCUMENT_PATTERNS.items()
    }
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Unknown"
