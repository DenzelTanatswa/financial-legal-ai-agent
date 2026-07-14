from pathlib import Path
from Utilis.pdf_reader import extract_pdf_text
from Utilis.docx_reader import extract_docx_text
from Utilis.text_cleaner import clean_text
import pandas as pd


def extract_text(filepath):
    ext = Path(filepath).suffix.lower()

    if ext == ".pdf":
        raw = extract_pdf_text(filepath)
    elif ext == ".docx":
        raw = extract_docx_text(filepath)
    elif ext == ".txt":
        raw = Path(filepath).read_text(encoding="utf-8", errors="ignore")
    elif ext == ".csv":
        df = pd.read_csv(filepath)
        raw = df.to_string(index=False)
    elif ext == ".xlsx":
        df = pd.read_excel(filepath)
        raw = df.to_string(index=False)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    return clean_text(raw)
