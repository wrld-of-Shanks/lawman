"""
Legal Document Processor using OpenNyAI
Provides Indian legal text processing capabilities including NER, Rhetorical Role classification, and Summarization
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio
from concurrent.futures import ThreadPoolExecutor
import traceback

try:
    from opennyai import Pipeline
    from opennyai.utils import Data
    OPENNYAI_AVAILABLE = True
except ImportError:
    OPENNYAI_AVAILABLE = False
    logging.warning("OpenNyAI not available. Install with: pip install opennyai")

@dataclass
class LegalAnalysisResult:
    """Result of legal document analysis"""
    entities: List[Dict[str, Any]]
    rhetorical_roles: List[Dict[str, Any]]
    summary: Dict[str, str]
    processed_text: str
    error: Optional[str] = None

class LegalProcessor:
    """
    Legal document processor using OpenNyAI for Indian legal texts
    Provides NER, Rhetorical Role classification, and Summarization
    """
    
    def __init__(self, use_gpu: bool = False, components: List[str] = None):
        """
        Initialize the legal processor
        
        Args:
            use_gpu: Whether to use GPU acceleration
            components: List of components to use ['NER', 'Rhetorical_Role', 'Summarizer']
        """
        self.use_gpu = use_gpu
        self.components = components or ['NER', 'Rhetorical_Role', 'Summarizer']
        self.pipeline = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        if not OPENNYAI_AVAILABLE:
            logging.error("OpenNyAI is not installed. Legal processing will be limited.")
            return
            
        try:
            self._initialize_pipeline()
        except Exception as e:
            logging.error(f"Failed to initialize OpenNyAI pipeline: {str(e)}")
            self.pipeline = None
    
    def _initialize_pipeline(self):
        """Initialize the OpenNyAI pipeline"""
        if not OPENNYAI_AVAILABLE:
            return
            
        try:
            self.pipeline = Pipeline(
                components=self.components,
                use_gpu=self.use_gpu,
                verbose=False
            )
            logging.info(f"OpenNyAI pipeline initialized with components: {self.components}")
        except Exception as e:
            logging.error(f"Pipeline initialization failed: {str(e)}")
            raise
    
    def _process_text_sync(self, text: str) -> LegalAnalysisResult:
        """
        Synchronous text processing (runs in thread pool)
        
        Args:
            text: Legal document text to process
            
        Returns:
            LegalAnalysisResult with extracted information
        """
        if not self.pipeline:
            return LegalAnalysisResult(
                entities=[],
                rhetorical_roles=[],
                summary={},
                processed_text=text,
                error="OpenNyAI pipeline not available"
            )
        
        try:
            # Prepare data for OpenNyAI
            data = Data([text])
            
            # Process with pipeline
            results = self.pipeline(data)
            
            if not results or len(results) == 0:
                return LegalAnalysisResult(
                    entities=[],
                    rhetorical_roles=[],
                    summary={},
                    processed_text=text,
                    error="No results from OpenNyAI pipeline"
                )
            
            result = results[0]
            
            # Extract entities from annotations
            entities = []
            rhetorical_roles = []
            
            if 'annotations' in result:
                for annotation in result['annotations']:
                    # Extract named entities
                    if 'entities' in annotation:
                        for entity in annotation['entities']:
                            entities.append({
                                'text': entity.get('text', ''),
                                'label': entity.get('label', ''),
                                'start': entity.get('start', 0),
                                'end': entity.get('end', 0),
                                'confidence': entity.get('confidence', 0.0)
                            })
                    
                    # Extract rhetorical roles
                    if 'rhetorical_role' in annotation:
                        rhetorical_roles.append({
                            'sentence': annotation.get('sentence', ''),
                            'role': annotation.get('rhetorical_role', ''),
                            'confidence': annotation.get('rr_confidence', 0.0)
                        })
            
            # Extract summary
            summary = result.get('summary', {})
            
            return LegalAnalysisResult(
                entities=entities,
                rhetorical_roles=rhetorical_roles,
                summary=summary,
                processed_text=text
            )
            
        except Exception as e:
            logging.error(f"Error processing legal text: {str(e)}")
            logging.error(traceback.format_exc())
            return LegalAnalysisResult(
                entities=[],
                rhetorical_roles=[],
                summary={},
                processed_text=text,
                error=str(e)
            )
    
    async def process_text(self, text: str) -> LegalAnalysisResult:
        """
        Asynchronously process legal document text
        
        Args:
            text: Legal document text to process
            
        Returns:
            LegalAnalysisResult with extracted information
        """
        if not text or not text.strip():
            return LegalAnalysisResult(
                entities=[],
                rhetorical_roles=[],
                summary={},
                processed_text="",
                error="Empty text provided"
            )
        
        # Run the synchronous processing in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor, 
            self._process_text_sync, 
            text
        )
        
        return result
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from legal text (synchronous)
        
        Args:
            text: Legal document text
            
        Returns:
            List of extracted entities
        """
        result = self._process_text_sync(text)
        return result.entities
    
    def get_rhetorical_structure(self, text: str) -> List[Dict[str, Any]]:
        """
        Get rhetorical role structure of legal document (synchronous)
        
        Args:
            text: Legal document text
            
        Returns:
            List of sentences with rhetorical roles
        """
        result = self._process_text_sync(text)
        return result.rhetorical_roles
    
    def summarize_document(self, text: str) -> Dict[str, str]:
        """
        Generate extractive summary of legal document (synchronous)
        
        Args:
            text: Legal document text
            
        Returns:
            Dictionary with summary by rhetorical roles
        """
        result = self._process_text_sync(text)
        return result.summary
    
    def get_legal_insights(self, text: str) -> Dict[str, Any]:
        """
        Get comprehensive legal insights from document
        
        Args:
            text: Legal document text
            
        Returns:
            Dictionary with all extracted information
        """
        result = self._process_text_sync(text)
        
        return {
            'entities': result.entities,
            'rhetorical_structure': result.rhetorical_roles,
            'summary': result.summary,
            'entity_counts': self._count_entities(result.entities),
            'key_provisions': self._extract_provisions(result.entities),
            'precedents': self._extract_precedents(result.entities),
            'error': result.error
        }
    
    def _count_entities(self, entities: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count entities by type"""
        counts = {}
        for entity in entities:
            label = entity.get('label', 'UNKNOWN')
            counts[label] = counts.get(label, 0) + 1
        return counts
    
    def _extract_provisions(self, entities: List[Dict[str, Any]]) -> List[str]:
        """Extract legal provisions from entities"""
        provisions = []
        for entity in entities:
            if entity.get('label') in ['PROVISION', 'STATUTE', 'ACT']:
                provisions.append(entity.get('text', ''))
        return list(set(provisions))  # Remove duplicates
    
    def _extract_precedents(self, entities: List[Dict[str, Any]]) -> List[str]:
        """Extract legal precedents from entities"""
        precedents = []
        for entity in entities:
            if entity.get('label') in ['PRECEDENT', 'CASE_NAME']:
                precedents.append(entity.get('text', ''))
        return list(set(precedents))  # Remove duplicates
    
    def is_available(self) -> bool:
        """Check if OpenNyAI is available and pipeline is initialized"""
        return OPENNYAI_AVAILABLE and self.pipeline is not None
    
    def get_status(self) -> Dict[str, Any]:
        """Get processor status information"""
        return {
            'opennyai_available': OPENNYAI_AVAILABLE,
            'pipeline_initialized': self.pipeline is not None,
            'components': self.components,
            'use_gpu': self.use_gpu
        }

# Global processor instance
_legal_processor = None

def get_legal_processor() -> LegalProcessor:
    """Get global legal processor instance"""
    global _legal_processor
    if _legal_processor is None:
        _legal_processor = LegalProcessor(use_gpu=False)  # Set to True if GPU available
    return _legal_processor

# Convenience functions for direct use
async def analyze_legal_text(text: str) -> LegalAnalysisResult:
    """Analyze legal text and return comprehensive results"""
    processor = get_legal_processor()
    return await processor.process_text(text)

def extract_legal_entities(text: str) -> List[Dict[str, Any]]:
    """Extract named entities from legal text"""
    processor = get_legal_processor()
    return processor.extract_entities(text)

def get_document_structure(text: str) -> List[Dict[str, Any]]:
    """Get rhetorical structure of legal document"""
    processor = get_legal_processor()
    return processor.get_rhetorical_structure(text)

def summarize_legal_document(text: str) -> Dict[str, str]:
    """Generate summary of legal document"""
    processor = get_legal_processor()
    return processor.summarize_document(text)
