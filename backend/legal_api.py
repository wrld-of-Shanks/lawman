from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from pydantic import BaseModel
from document_processor import document_processor
from legal_analysis import legal_analyzer
import logging

logger = logging.getLogger(__name__)
legal_router = APIRouter()

class AnalysisRequest(BaseModel):
    text: str
    doc_type: str
    action: str  # summarize, translate, verify
    target_lang: str = "Hindi"  # For translation

@legal_router.get("/legal")
async def get_legal_info():
    return {"message": "Legal API endpoint"}

@legal_router.post("/upload_doc")
async def upload_document(file: UploadFile = File(...)):
    try:
        # 1. Save file
        file_path = document_processor.save_upload(file)
        
        # 2. Extract text
        text = document_processor.extract_text(file_path)
        
        # 3. Identify type
        doc_type = legal_analyzer.identify_document_type(text)
        
        # 4. Cleanup file immediately (Privacy)
        document_processor.cleanup(file_path)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from document. Ensure it is a valid text-based PDF, DOCX, or clear Image.")
            
        return {
            "text": text,
            "doc_type": doc_type,
            "filename": file.filename
        }
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@legal_router.post("/analyze_doc")
async def analyze_document(request: AnalysisRequest):
    try:
        if request.action == "summarize":
            result = legal_analyzer.summarize_document(request.text, request.doc_type)
            return result
            
        elif request.action == "translate":
            translation = legal_analyzer.translate_document(request.text, request.target_lang)
            return {"translation": translation}
            
        elif request.action == "verify":
            verification = legal_analyzer.verify_legality(request.text, request.doc_type)
            return verification
            
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
            
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
