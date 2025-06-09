import openai
from typing import Dict, List, Any, Optional
import logging
import json
import os
from dotenv import load_dotenv
from .model_manager import ModelManager

load_dotenv()

class LLMAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model_manager = ModelManager()
        self.default_api_key = os.getenv('OPENAI_API_KEY')
        self.default_anthropic_key = os.getenv('ANTHROPIC_API_KEY')

    def analyze_tax_documents(self, 
                            documents: List[Dict[str, Any]], 
                            use_case: str = 'complex_analysis',
                            user_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze tax documents using LLM to extract insights and potential audit risks
        """
        try:
            # Get appropriate model configuration
            model_config = self._get_model_config(use_case, user_settings)
            
            # Set API key based on user settings
            self._set_api_keys(user_settings)
            
            # Prepare documents for analysis
            document_texts = self._prepare_documents(documents)
            
            # Get initial analysis
            initial_analysis = self._get_initial_analysis(document_texts, model_config)
            
            # Get detailed risk assessment
            risk_assessment = self._get_risk_assessment(initial_analysis, model_config)
            
            # Get specific recommendations
            recommendations = self._get_recommendations(risk_assessment, model_config)
            
            # Calculate cost and token usage
            cost_analysis = self._calculate_analysis_cost(
                document_texts, 
                initial_analysis, 
                risk_assessment, 
                recommendations,
                model_config
            )
            
            return {
                'analysis': initial_analysis,
                'risk_assessment': risk_assessment,
                'recommendations': recommendations,
                'model_used': model_config['name'],
                'cost_analysis': cost_analysis,
                'api_used': 'user' if user_settings and user_settings.get('openai_api_key') else 'service'
            }
        except Exception as e:
            self.logger.error(f"Error in LLM analysis: {str(e)}")
            raise
        finally:
            # Reset to default API key
            self._reset_api_keys()

    def _get_model_config(self, 
                         use_case: str, 
                         user_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get model configuration based on use case and user settings"""
        if user_settings:
            # Check if user's preferred model is available for their tier
            preferred_model = user_settings.get('preferred_model')
            subscription_tier = user_settings.get('subscription_tier', 'free')
            
            if preferred_model and self.model_manager.can_use_model(subscription_tier, preferred_model):
                return self.model_manager.models[preferred_model]
        
        # Fall back to default model for use case
        return self.model_manager.get_model_config(use_case)

    def _set_api_keys(self, user_settings: Optional[Dict[str, Any]] = None):
        """Set API keys based on user settings"""
        if user_settings:
            if user_settings.get('openai_api_key'):
                openai.api_key = user_settings['openai_api_key']
            if user_settings.get('anthropic_api_key'):
                # Set Anthropic API key if needed
                pass

    def _reset_api_keys(self):
        """Reset API keys to default"""
        openai.api_key = self.default_api_key

    def _prepare_documents(self, documents: List[Dict[str, Any]]) -> str:
        """Prepare documents for LLM analysis"""
        prepared_text = "Tax Documents Analysis:\n\n"
        
        for doc in documents:
            prepared_text += f"Document Type: {doc.get('type', 'Unknown')}\n"
            prepared_text += f"Content: {doc.get('content', '')}\n"
            prepared_text += f"Amount: {doc.get('amount', 0)}\n"
            prepared_text += f"Date: {doc.get('date', 'Unknown')}\n\n"
        
        return prepared_text

    def _get_initial_analysis(self, 
                            document_text: str, 
                            model_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get initial analysis of tax documents"""
        prompt = f"""
        Analyze the following tax documents and provide insights:
        
        {document_text}
        
        Please provide:
        1. Key financial patterns
        2. Unusual transactions
        3. Potential inconsistencies
        4. Notable deductions
        5. Income patterns
        
        Format the response as a JSON object.
        """
        
        response = openai.ChatCompletion.create(
            model=model_config['name'],
            messages=[
                {"role": "system", "content": "You are a tax analysis expert. Analyze the provided tax documents and identify key patterns, risks, and insights."},
                {"role": "user", "content": prompt}
            ],
            temperature=model_config['temperature'],
            max_tokens=model_config['max_tokens']
        )
        
        return json.loads(response.choices[0].message.content)

    def _get_risk_assessment(self, 
                           initial_analysis: Dict[str, Any], 
                           model_config: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed risk assessment based on initial analysis"""
        prompt = f"""
        Based on the following tax analysis, provide a detailed risk assessment:
        
        {json.dumps(initial_analysis, indent=2)}
        
        Please provide:
        1. Overall audit risk score (0-1)
        2. Specific risk factors
        3. Risk level (Very Low, Low, Medium, High, Very High)
        4. Confidence score in the assessment
        
        Format the response as a JSON object.
        """
        
        response = openai.ChatCompletion.create(
            model=model_config['name'],
            messages=[
                {"role": "system", "content": "You are a tax risk assessment expert. Evaluate the provided analysis and determine audit risk factors."},
                {"role": "user", "content": prompt}
            ],
            temperature=model_config['temperature'],
            max_tokens=model_config['max_tokens']
        )
        
        return json.loads(response.choices[0].message.content)

    def _get_recommendations(self, 
                           risk_assessment: Dict[str, Any], 
                           model_config: Dict[str, Any]) -> List[str]:
        """Get specific recommendations based on risk assessment"""
        prompt = f"""
        Based on the following risk assessment, provide specific recommendations:
        
        {json.dumps(risk_assessment, indent=2)}
        
        Please provide:
        1. Immediate actions to reduce audit risk
        2. Documentation improvements
        3. Long-term strategies
        4. Professional consultation recommendations
        
        Format the response as a JSON array of recommendations.
        """
        
        response = openai.ChatCompletion.create(
            model=model_config['name'],
            messages=[
                {"role": "system", "content": "You are a tax optimization expert. Provide specific, actionable recommendations to reduce audit risk."},
                {"role": "user", "content": prompt}
            ],
            temperature=model_config['temperature'],
            max_tokens=model_config['max_tokens']
        )
        
        return json.loads(response.choices[0].message.content)

    def analyze_specific_risk(self, 
                            document: Dict[str, Any], 
                            risk_type: str,
                            use_case: str = 'complex_analysis') -> Dict[str, Any]:
        """
        Analyze a specific risk type for a given document
        """
        model_config = self.model_manager.get_model_config(use_case)
        
        prompt = f"""
        Analyze the following document for {risk_type} risk:
        
        Document Type: {document.get('type', 'Unknown')}
        Content: {document.get('content', '')}
        Amount: {document.get('amount', 0)}
        Date: {document.get('date', 'Unknown')}
        
        Please provide:
        1. Risk level for this specific document
        2. Specific concerns
        3. Supporting evidence
        4. Mitigation strategies
        
        Format the response as a JSON object.
        """
        
        response = openai.ChatCompletion.create(
            model=model_config['name'],
            messages=[
                {"role": "system", "content": f"You are a tax risk analysis expert specializing in {risk_type}."},
                {"role": "user", "content": prompt}
            ],
            temperature=model_config['temperature'],
            max_tokens=model_config['max_tokens']
        )
        
        return json.loads(response.choices[0].message.content)

    def _calculate_analysis_cost(self,
                               document_text: str,
                               initial_analysis: Dict[str, Any],
                               risk_assessment: Dict[str, Any],
                               recommendations: List[str],
                               model_config: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate the estimated cost and token usage of the analysis"""
        # Estimate tokens (rough approximation)
        input_tokens = len(document_text.split()) * 1.3  # Words to tokens
        output_tokens = (
            len(json.dumps(initial_analysis)) +
            len(json.dumps(risk_assessment)) +
            len(json.dumps(recommendations))
        ) / 4  # Characters to tokens
        
        total_tokens = int(input_tokens + output_tokens)
        cost = self.model_manager.estimate_cost(
            int(input_tokens),
            int(output_tokens),
            model_config['name']
        )
        
        return {
            'input_tokens': int(input_tokens),
            'output_tokens': int(output_tokens),
            'total_tokens': total_tokens,
            'estimated_cost': cost,
            'cost_per_token': cost / total_tokens if total_tokens > 0 else 0
        } 