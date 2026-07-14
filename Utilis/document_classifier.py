import re


DOCUMENT_PATTERNS = {

    "Bank Statement": [
        r"available balance",
        r"transaction",
        r"account number",
        r"withdrawal",
        r"deposit",
        r"bank statement",
        r"opening balance"
    ],

    "Invoice": [
        r"invoice",
        r"invoice number",
        r"due date",
        r"vat",
        r"subtotal",
        r"total amount"
    ],

    "Contract": [
        r"agreement",
        r"party",
        r"contract",
        r"termination",
        r"governing law",
        r"effective date"
    ],

    "Tax Document": [
        r"tax",
        r"income",
        r"deduction",
        r"taxpayer",
        r"return"
    ]
}


def classify_document(text):

    text = text.lower()

    scores = {}

    for doc_type, patterns in DOCUMENT_PATTERNS.items():

        score = 0

        for pattern in patterns:

            if re.search(pattern, text):
                score += 1

        scores[doc_type] = score

    best = max(scores, key=scores.get)

    if scores[best] == 0:
        return "Unknown"

    return best