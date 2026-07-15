import re


def _unique(lst):
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]


def extract_entities(text):
    amount_pattern = r"\$[\d,]+(?:\.\d{1,2})?|\b\d{1,3}(?:,\d{3})+(?:\.\d{1,2})?\b"
    date_pattern   = r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
    email_pattern  = r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"

    return {
        "Amounts": _unique(re.findall(amount_pattern, text)),
        "Dates":   _unique(re.findall(date_pattern,   text)),
        "Emails":  _unique(re.findall(email_pattern,  text)),
    }
