from docx import Document

def text_to_docx(text: str) -> Document:
    doc = Document()
    for line in text.split("\n"):
        if line.strip():
            doc.add_paragraph(line.strip())
    return doc