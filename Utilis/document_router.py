ROUTES = {
    "Bank Statement": "Financial Analyst",
    "Invoice":        "Invoice Analyzer",
    "Contract":       "Contract Reviewer",
    "Tax Document":   "Tax Assistant",
    "Unknown":        "General Assistant",
}


def route_document(document_type):
    return ROUTES.get(document_type, "General Assistant")
