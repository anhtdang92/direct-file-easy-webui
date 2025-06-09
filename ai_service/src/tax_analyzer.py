from typing import Dict, Any, List
import logging
from .analyzers.analyzer_factory import AnalyzerFactory

logger = logging.getLogger(__name__)

class TaxAnalyzer:
    def __init__(self):
        self.analyzer_factory = AnalyzerFactory()
    
    def analyze_document(self, doc_type: str, text: str, image: Any = None) -> Dict[str, Any]:
        """
        Analyze a tax document using the appropriate analyzer.
        
        Args:
            doc_type: Type of document (e.g., 'w2', '1099')
            text: OCR extracted text from document
            image: Optional image data for additional analysis
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            analyzer = self.analyzer_factory.get_analyzer(doc_type)
            return analyzer.analyze(text, image)
        except ValueError as e:
            logger.error(f"Error getting analyzer: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def combine_analyses(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combine multiple document analyses into a comprehensive tax analysis.
        
        Args:
            analyses: List of individual document analyses
            
        Returns:
            Combined tax analysis
        """
        try:
            combined = {
                'success': True,
                'total_income': 0.0,
                'total_taxes_withheld': 0.0,
                'documents': [],
                'tax_implications': [],
                'recommendations': []
            }
            
            # Process each analysis
            for analysis in analyses:
                if not analysis.get('success', False):
                    continue
                
                # Add document summary
                combined['documents'].append({
                    'type': analysis.get('type'),
                    'form_type': analysis.get('form_type'),
                    'totals': analysis.get('totals', {})
                })
                
                # Add totals
                totals = analysis.get('totals', {})
                combined['total_income'] += totals.get('total_income', 0.0)
                combined['total_taxes_withheld'] += totals.get('total_taxes_withheld', 0.0)
                
                # Add insights
                insights = analysis.get('insights', {})
                combined['tax_implications'].extend(insights.get('tax_implications', []))
                combined['recommendations'].extend(insights.get('recommendations', []))
            
            # Generate overall recommendations
            self._generate_overall_recommendations(combined)
            
            return combined
            
        except Exception as e:
            logger.error(f"Error combining analyses: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_overall_recommendations(self, analysis: Dict[str, Any]) -> None:
        """Generate overall tax recommendations based on combined analysis."""
        # Check if estimated tax payments might be needed
        if analysis['total_income'] > 0:
            estimated_tax = analysis['total_income'] * 0.3  # Rough estimate
            if estimated_tax > analysis['total_taxes_withheld']:
                analysis['recommendations'].append({
                    'type': 'estimated_tax',
                    'message': 'Consider making estimated tax payments to avoid underpayment penalties',
                    'priority': 'high'
                })
        
        # Check for potential deductions
        if analysis['total_income'] > 50000:
            analysis['recommendations'].append({
                'type': 'deductions',
                'message': 'Consider consulting a tax professional about potential deductions',
                'priority': 'medium'
            })
        
        # Sort recommendations by priority
        analysis['recommendations'].sort(
            key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x.get('priority', 'low'), 3)
        ) 