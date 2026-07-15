from docx import Document


def extract_docx_text(docx_path):
    doc = Document(str(docx_path))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
