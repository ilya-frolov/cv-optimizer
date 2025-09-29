from docx import Document

def extract_cv_text(path: str) -> str:
    doc = Document(path)
    
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])