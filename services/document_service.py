from pathlib import Path
import pandas as pd
import re
from werkzeug.utils import secure_filename
from core.config import UPLOAD_FOLDER
from core.models import ClassificationResult, EntityExtractionResult

_UPLOAD_ROOT = Path(UPLOAD_FOLDER).resolve()
_UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

_DOCUMENT_PATTERNS = {
    "Bank Statement": [r"available balance", r"transaction", r"account number", r"withdrawal", r"deposit", r"bank statement", r"opening balance"],
    "Invoice":        [r"invoice", r"invoice number", r"due date", r"vat", r"subtotal", r"total amount"],
    "Contract":       [r"agreement", r"party", r"contract", r"termination", r"governing law", r"effective date"],
    "Tax Document":   [r"tax", r"income", r"deduction", r"taxpayer", r"return"],
}

_ROUTES = {
    "Bank Statement": "Financial Analyst",
    "Invoice":        "Invoice Analyzer",
    "Contract":       "Contract Reviewer",
    "Tax Document":   "Tax Assistant",
    "Unknown":        "General Assistant",
}


def save_uploaded_file(uploaded_file) -> str:
    safe_name = secure_filename(uploaded_file.name)
    if not safe_name:
        raise ValueError("Invalid filename.")
    filepath = _UPLOAD_ROOT / safe_name
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(filepath)


def extract_text(filepath: str) -> str:
    path = Path(filepath).resolve()
    if not str(path).startswith(str(_UPLOAD_ROOT)):
        raise ValueError(f"Access denied: '{filepath}' is outside the upload directory.")
    ext = path.suffix.lower()
    if ext == ".pdf":
        import fitz
        with fitz.open(str(path)) as doc:
            raw = "".join(page.get_text() for page in doc)
    elif ext == ".docx":
        from docx import Document
        raw = "\n".join(p.text for p in Document(str(path)).paragraphs if p.text.strip())
    elif ext == ".txt":
        raw = path.read_text(encoding="utf-8", errors="ignore")
    elif ext == ".csv":
        raw = pd.read_csv(path).to_string(index=False)
    elif ext == ".xlsx":
        raw = pd.read_excel(path).to_string(index=False)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
    return _clean_text(raw)


def classify_document(text: str) -> ClassificationResult:
    """Classify from rule signals and return a heuristic confidence indicator."""
    lower = text.lower()
    matches = {
        doc_type: [p for p in patterns if re.search(p, lower)]
        for doc_type, patterns in _DOCUMENT_PATTERNS.items()
    }
    scores = {doc_type: len(patterns) for doc_type, patterns in matches.items()}
    best = max(scores, key=scores.get)
    best_score = scores[best]
    if best_score == 0:
        return ClassificationResult.from_score("Unknown", 0.2, [])

    # Coverage is tempered by the margin over the next-best document type.
    coverage = best_score / len(_DOCUMENT_PATTERNS[best])
    runner_up = sorted(scores.values(), reverse=True)[1]
    separation = (best_score - runner_up) / max(best_score, 1)
    score = 0.45 + (0.35 * coverage) + (0.20 * separation)
    return ClassificationResult.from_score(best, score, matches[best])


def route_document(document_type: str) -> str:
    return _ROUTES.get(document_type, "General Assistant")


def extract_entities(text: str) -> EntityExtractionResult:
    """Extract pattern-backed entities with a non-probabilistic quality signal."""
    def _unique(lst):
        seen = set()
        return [x for x in lst if not (x in seen or seen.add(x))]
    entities = {
        "Amounts": _unique(re.findall(r"\$[\d,]+(?:\.\d{1,2})?|\b\d{1,3}(?:,\d{3})+(?:\.\d{1,2})?\b", text)),
        "Dates":   _unique(re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", text)),
        "Emails":  _unique(re.findall(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", text)),
    }
    populated_types = sum(bool(values) for values in entities.values())
    entity_count = sum(len(values) for values in entities.values())
    # More independent pattern matches increase reliability, with a conservative cap.
    score = min(0.92, 0.25 + (0.18 * populated_types) + (0.035 * min(entity_count, 8)))
    return EntityExtractionResult.from_score(entities, score)


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()
