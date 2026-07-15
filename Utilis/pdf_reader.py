import fitz


def extract_pdf_text(pdf_path):
    with fitz.open(str(pdf_path)) as doc:
        return "".join(page.get_text() for page in doc)
