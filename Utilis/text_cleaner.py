import re
import unicodedata


def clean_text(text):
    # Normalize unicode (e.g. ligatures, smart quotes)
    text = unicodedata.normalize("NFKD", text)
    # Strip non-ASCII
    text = text.encode("ascii", errors="ignore").decode("ascii")
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text
