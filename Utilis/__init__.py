from pathlib import Path
import pandas as pd
from Utilis.pdf_reader import extract_pdf_text
from Utilis.docx_reader import extract_docx_text
from Utilis.text_cleaner import clean_text

# Resolve the trusted upload root once at import time
_UPLOAD_ROOT = Path("Uploads").resolve()


def extract_text(filepath):
    path = Path(filepath).resolve()

    # Guard against path traversal — ensure file is inside the upload folder
    if not str(path).startswith(str(_UPLOAD_ROOT)):
        raise ValueError(f"Access denied: '{filepath}' is outside the upload directory.")

    ext = path.suffix.lower()

    if ext == ".pdf":
        raw = extract_pdf_text(path)
    elif ext == ".docx":
        raw = extract_docx_text(path)
    elif ext == ".txt":
        raw = path.read_text(encoding="utf-8", errors="ignore")
    elif ext == ".csv":
        raw = pd.read_csv(path).to_string(index=False)
    elif ext == ".xlsx":
        raw = pd.read_excel(path).to_string(index=False)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    return clean_text(raw)
