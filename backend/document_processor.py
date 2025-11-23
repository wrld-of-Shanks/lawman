"""
Document Processor Module
Handles OCR, text extraction, and file management for legal documents.
Supports: PDF, DOCX, TXT, PNG, JPG
"""

import os
import logging
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import PyPDF2
import docx
from pathlib import Path
import shutil
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory for temporary file storage
UPLOAD_DIR = Path("./temp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class DocumentProcessor:
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg']
        
    def save_upload(self, upload_file) -> Path:
        """Save uploaded file to temp directory with unique name"""
        file_ext = Path(upload_file.filename).suffix.lower()
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}")
            
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / unique_filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
            
        return file_path

    def extract_text(self, file_path: Path) -> str:
        """Extract text from file based on extension"""
        ext = file_path.suffix.lower()
        
        try:
            if ext == '.txt':
                return self._read_txt(file_path)
            elif ext == '.docx':
                return self._read_docx(file_path)
            elif ext == '.pdf':
                return self._read_pdf(file_path)
            elif ext in ['.png', '.jpg', '.jpeg']:
                return self._ocr_image(file_path)
            else:
                return ""
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            raise

    def _read_txt(self, path: Path) -> str:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def _read_docx(self, path: Path) -> str:
        doc = docx.Document(path)
        return "\n".join([para.text for para in doc.paragraphs])

    def _read_pdf(self, path: Path) -> str:
        text = ""
        # First try digital extraction
        try:
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.warning(f"Digital PDF extraction failed: {e}")

        # If text is empty or very short, it might be a scanned PDF -> use OCR
        if len(text.strip()) < 50:
            logger.info("PDF appears to be scanned. Attempting OCR...")
            try:
                images = convert_from_path(str(path))
                for img in images:
                    text += pytesseract.image_to_string(img) + "\n"
            except Exception as e:
                logger.error(f"OCR failed (Tesseract might be missing): {e}")
                if not text:
                    return "[ERROR: Could not extract text. This appears to be a scanned document, but OCR tools are not available on the server.]"
        
        return text

    def _ocr_image(self, path: Path) -> str:
        try:
            image = Image.open(path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            logger.error(f"Image OCR failed: {e}")
            return "[ERROR: OCR failed. Please ensure Tesseract is installed on the server.]"

    def cleanup(self, file_path: Path):
        """Securely delete the file"""
        try:
            if file_path.exists():
                os.remove(file_path)
                logger.info(f"Deleted temp file: {file_path}")
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")

document_processor = DocumentProcessor()
