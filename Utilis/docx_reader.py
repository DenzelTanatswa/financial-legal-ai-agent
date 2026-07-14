from docx import Document


def extract_docx_text(docx_path):

    document = Document(docx_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        paragraphs.append(paragraph.text)

    return "\n".join(paragraphs)