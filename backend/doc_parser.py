import os
from typing import List

# Make imports optional to avoid dependency issues
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    from docx import Document
except ImportError:
    Document = None

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file."""
    if fitz is None:
        return f"[PDF CONTENT FROM: {pdf_path}]"
    
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        text = f"[Error reading PDF: {str(e)}]"
    return text

def extract_text_from_docx(docx_path: str) -> str:
    """Extract text from a DOCX file."""
    if Document is None:
        return f"[DOCX CONTENT FROM: {docx_path}]"
    
    try:
        doc = Document(docx_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        return f"[Error reading DOCX: {str(e)}]"

def extract_text_from_txt(txt_path: str) -> str:
    with open(txt_path, 'r', encoding='utf-8') as f:
        return f.read()

def chunk_text(text: str, chunk_size: int = 150) -> List[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

def parse_and_chunk(file_path: str) -> List[str]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif ext == '.docx':
        text = extract_text_from_docx(file_path)
    elif ext == '.txt':
        text = extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    return chunk_text(text)