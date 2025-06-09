from typing import Dict, Any, Type
from .w2_analyzer import W2Analyzer
from .form1099_analyzer import Form1099Analyzer

class AnalyzerFactory:
    """Factory class for creating document analyzers."""
    
    _analyzers: Dict[str, Type] = {
        'w2': W2Analyzer,
        '1099': Form1099Analyzer
    }
    
    @classmethod
    def get_analyzer(cls, doc_type: str) -> Any:
        """
        Get the appropriate analyzer for the document type.
        
        Args:
            doc_type: Type of document to analyze
            
        Returns:
            Instance of the appropriate analyzer
            
        Raises:
            ValueError: If document type is not supported
        """
        analyzer_class = cls._analyzers.get(doc_type.lower())
        if not analyzer_class:
            raise ValueError(f"Unsupported document type: {doc_type}")
        
        return analyzer_class()
    
    @classmethod
    def register_analyzer(cls, doc_type: str, analyzer_class: Type) -> None:
        """
        Register a new document analyzer.
        
        Args:
            doc_type: Type of document the analyzer handles
            analyzer_class: Class of the analyzer to register
        """
        cls._analyzers[doc_type.lower()] = analyzer_class
    
    @classmethod
    def get_supported_types(cls) -> list:
        """Get list of supported document types."""
        return list(cls._analyzers.keys()) 