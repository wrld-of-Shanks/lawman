"""
Legal Analysis Module
Handles Summarization, Translation, and Verification of legal documents using LLM.
"""

import logging
from typing import Dict, List, Optional
from local_llm import generate_with_context

logger = logging.getLogger(__name__)

class LegalAnalyzer:
    def __init__(self):
        pass

    def identify_document_type(self, text: str) -> str:
        """Identify the type of legal document"""
        prompt = f"""
        Analyze the following legal document text and identify its type.
        Examples: Contract, FIR, Affidavit, Rent Agreement, Sale Deed, Marriage Certificate, Cheque Bounce Notice, Legal Notice, etc.
        
        Return ONLY the document type name. If unsure, return "Unknown Legal Document".
        
        Document Text (first 500 chars):
        {text[:500]}...
        """
        response = generate_with_context("You are a legal document classifier.", prompt, temperature=0.1)
        return response.strip()

    def summarize_document(self, text: str, doc_type: str) -> Dict:
        """
        Generate a legal summary with extracted entities.
        """
        system_prompt = """
        You are an expert legal AI assistant. Your task is to summarize legal documents accurately and conservatively.
        Do not hallucinate facts. If a detail is missing, do not invent it.
        """
        
        user_prompt = f"""
        Document Type: {doc_type}
        
        Please provide a comprehensive legal summary of the following document.
        
        Structure your response as follows:
        1. **Executive Summary** (200-300 words): A clear, professional summary of the document's purpose and key content.
        2. **Key Entities**: List names, addresses, dates, case numbers, court names, etc.
        3. **Important Clauses/Facts**: Bullet points of the most critical legal obligations or facts.
        
        Document Text:
        {text[:10000]} 
        (Text truncated if too long)
        """
        
        summary = generate_with_context(system_prompt, user_prompt, temperature=0.2)
        
        return {
            "summary": summary,
            "doc_type": doc_type
        }

    def translate_document(self, text: str, target_lang: str) -> str:
        """
        Translate legal document preserving legal meaning.
        """
        system_prompt = f"""
        You are an expert legal translator. Translate the following legal document into {target_lang}.
        Maintain strict legal accuracy. Preserve Latin terms or specific legal terminology where appropriate, or provide the standard equivalent in the target language.
        Do not summarize; translate the full meaning.
        """
        
        user_prompt = f"""
        Translate this legal text to {target_lang}:
        
        {text[:8000]}
        """
        
        translation = generate_with_context(system_prompt, user_prompt, temperature=0.1)
        return translation

    def verify_legality(self, text: str, doc_type: str) -> Dict:
        """
        Verify the legality and completeness of the document.
        """
        system_prompt = """
        You are a senior legal compliance officer. Review the document for legal validity, completeness, and admissibility.
        """
        
        user_prompt = f"""
        Document Type: {doc_type}
        
        Analyze this document for the following:
        1. **Parties Identified**: Are all parties clearly named and identified?
        2. **Date & Jurisdiction**: Is the date and place of execution clear?
        3. **Signatures**: Does it indicate where signatures should be? (Note: OCR might miss handwritten signatures, so check for signature blocks).
        4. **Legal Formalities**: Stamp paper, notarization, witness clauses (if applicable for this doc type).
        5. **Ambiguity**: Is the language clear or ambiguous?
        
        Output your analysis in this specific JSON-like format (do not use actual JSON, just this structure):
        
        CHECKLIST:
        [✓/✗] Requirement 1
        [✓/✗] Requirement 2
        ...
        
        ANALYSIS:
        (Brief explanation of findings)
        
        VERDICT:
        (Choose exactly one: "Legally correct and ready for submission", "Needs modification before submission", "Likely invalid / inadmissible")
        
        CONFIDENCE:
        (0-100%)
        
        Document Text:
        {text[:10000]}
        """
        
        analysis = generate_with_context(system_prompt, user_prompt, temperature=0.1)
        
        # Parse the output to extract structured data (simple parsing)
        verdict = "Needs modification before submission"
        if "Legally correct and ready for submission" in analysis:
            verdict = "Legally correct and ready for submission"
        elif "Likely invalid" in analysis:
            verdict = "Likely invalid / inadmissible"
            
        return {
            "full_analysis": analysis,
            "verdict": verdict
        }

legal_analyzer = LegalAnalyzer()
