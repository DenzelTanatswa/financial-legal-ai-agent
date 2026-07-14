import re


def extract_entities(text):

    entities = {}

    amount_pattern = r"\$[\d,]+(?:\.\d{1,2})?|\b\d{1,3}(?:,\d{3})+(?:\.\d{1,2})?\b"

    date_pattern = r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"

    email_pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

    entities["Amounts"] = re.findall(amount_pattern, text)

    entities["Dates"] = re.findall(date_pattern, text)

    entities["Emails"] = re.findall(email_pattern, text)

    return entities