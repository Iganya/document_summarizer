from docx import Document
from io import BytesIO

# def extract_docx_text(content: bytes) -> str:
#     doc = Document(BytesIO(content))
#     return "\n".join(p.text for p in doc.paragraphs)

def extract_docx_text(content) -> str:
    doc = Document(BytesIO(content))
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    print(full_text)
    return "\n".join(full_text)
