from docx import Document


def extract_docx_text(docx_path):

    document = Document(docx_path)

    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]

    return "\n".join(paragraphs)