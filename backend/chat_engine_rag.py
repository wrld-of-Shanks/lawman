"""
Lightweight Chat Engine using Fuzzy Matching
Optimized for Render Free Tier (Low Memory Usage)
"""

import logging
from typing import Dict
from comprehensive_legal_db import get_comprehensive_legal_info, COMPREHENSIVE_LEGAL_FAQ

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def answer_query_with_rag(query: str, user_id: str = None, mode: str = "default") -> Dict:
    """
    Get answer using lightweight fuzzy matching instead of heavy Vector RAG.
    This prevents OOM crashes on free tier servers.
    """
    try:
        logger.info(f"Processing query: {query}")
        
        # 1. Try exact/keyword match from comprehensive DB
        answer = get_comprehensive_legal_info(query)
        
        if answer:
            return {
                "answer": answer,
                "sources": ["Legal Database"],
                "confidence": 0.9,
                "matched_question": query
            }
            
        # 2. Fuzzy Search (Fallback)
        # Split query into words and find best matching key in DB
        query_words = set(query.lower().split())
        best_match = None
        max_score = 0
        
        for key, value in COMPREHENSIVE_LEGAL_FAQ.items():
            key_words = set(key.replace('_', ' ').split())
            
            # Calculate overlap score
            overlap = len(query_words.intersection(key_words))
            if overlap > max_score:
                max_score = overlap
                best_match = value
        
        if best_match and max_score > 0:
            return {
                "answer": best_match,
                "sources": ["Legal Database (Fuzzy Match)"],
                "confidence": 0.7,
                "matched_question": query
            }

        # 3. No match found
        return {
            "answer": "I couldn't find specific information on that. Please try asking about topics like: bail, divorce, FIR, driving license, property, or consumer rights.",
            "sources": [],
            "confidence": 0.0,
            "matched_question": None
        }
        
    except Exception as e:
        logger.error(f"Error in chat engine: {str(e)}")
        return {
            "answer": "An error occurred. Please try asking about a specific legal topic.",
            "sources": [],
            "confidence": 0.0
        }
