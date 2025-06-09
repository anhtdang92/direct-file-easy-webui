from flask import Flask, request, jsonify
from flask_cors import CORS
from models.audit_risk_model import AuditRiskModel
from utils.feature_extractor import TaxFeatureExtractor
from utils.llm_analyzer import LLMAnalyzer
from utils.model_manager import ModelManager
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize models and analyzers
audit_model = AuditRiskModel()
feature_extractor = TaxFeatureExtractor()
llm_analyzer = LLMAnalyzer()
model_manager = ModelManager()

# Load pre-trained model (if available)
MODEL_PATH = os.getenv('MODEL_PATH', 'models/trained/audit_risk_model.joblib')
SCALER_PATH = os.getenv('SCALER_PATH', 'models/trained/audit_risk_scaler.joblib')

try:
    audit_model.load_model(MODEL_PATH, SCALER_PATH)
    logger.info("Pre-trained model loaded successfully")
except Exception as e:
    logger.warning(f"Could not load pre-trained model: {str(e)}")
    logger.info("Using untrained model")

@app.route('/api/analyze', methods=['POST'])
def analyze_documents():
    try:
        data = request.get_json()
        
        if not data or 'documents' not in data:
            return jsonify({
                'error': 'Missing required field: documents'
            }), 400
        
        # Extract user settings if provided
        user_settings = data.get('user_settings', {})
        
        # Validate user settings
        if user_settings:
            if not isinstance(user_settings, dict):
                return jsonify({
                    'error': 'user_settings must be a dictionary'
                }), 400
            
            # Validate API keys if provided
            if 'openai_api_key' in user_settings and not user_settings['openai_api_key']:
                return jsonify({
                    'error': 'Invalid OpenAI API key'
                }), 400
            
            if 'anthropic_api_key' in user_settings and not user_settings['anthropic_api_key']:
                return jsonify({
                    'error': 'Invalid Anthropic API key'
                }), 400
        
        # Get use case from request or default to complex analysis
        use_case = data.get('use_case', 'complex_analysis')
        
        # Validate use case
        if use_case not in ['quick_check', 'complex_analysis', 'detailed_review']:
            return jsonify({
                'error': 'Invalid use case. Must be one of: quick_check, complex_analysis, detailed_review'
            }), 400
        
        # Analyze documents
        result = llm_analyzer.analyze_tax_documents(
            documents=data['documents'],
            use_case=use_case,
            user_settings=user_settings
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/models', methods=['GET'])
def get_available_models():
    try:
        # Get subscription tier from query parameters
        subscription_tier = request.args.get('subscription_tier', 'free')
        
        # Get available models for the tier
        models = model_manager.get_available_models(subscription_tier)
        
        return jsonify({
            'models': models,
            'subscription_tier': subscription_tier
        })
    
    except Exception as e:
        logger.error(f"Error getting available models: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/cost-estimate', methods=['POST'])
def estimate_cost():
    try:
        data = request.get_json()
        
        if not data or 'documents' not in data:
            return jsonify({
                'error': 'Missing required field: documents'
            }), 400
        
        # Get model from request or default to GPT-3.5
        model = data.get('model', 'gpt-3.5-turbo')
        
        # Get use case
        use_case = data.get('use_case', 'complex_analysis')
        
        # Get model configuration
        model_config = model_manager.get_model_config(use_case)
        
        # Estimate tokens (rough approximation)
        document_text = ' '.join(str(doc) for doc in data['documents'])
        input_tokens = len(document_text.split()) * 1.3  # Words to tokens
        
        # Estimate output tokens based on use case
        output_tokens = {
            'quick_check': 500,
            'complex_analysis': 1000,
            'detailed_review': 2000
        }.get(use_case, 1000)
        
        # Calculate cost
        cost = model_manager.estimate_cost(
            int(input_tokens),
            output_tokens,
            model_config['name']
        )
        
        return jsonify({
            'estimated_input_tokens': int(input_tokens),
            'estimated_output_tokens': output_tokens,
            'estimated_total_tokens': int(input_tokens + output_tokens),
            'estimated_cost': cost,
            'model': model_config['name'],
            'use_case': use_case
        })
    
    except Exception as e:
        logger.error(f"Error estimating cost: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/ai/analyze', methods=['POST'])
def analyze_tax_data():
    """
    Analyze tax data and return comprehensive audit risk assessment
    """
    try:
        # Get tax data from request
        tax_data = request.json
        
        # Extract features for ML model
        features = feature_extractor.extract_features(tax_data)
        
        # Get ML-based audit risk score
        ml_risk_score = audit_model.predict_audit_risk(features)
        
        # Get LLM-based analysis
        llm_analysis = llm_analyzer.analyze_tax_documents(tax_data.get('documents', []))
        
        # Combine ML and LLM results
        combined_analysis = {
            'ml_analysis': {
                'audit_risk_score': ml_risk_score,
                'risk_level': _get_risk_level(ml_risk_score),
                'risk_factors': _get_risk_factors(tax_data, ml_risk_score),
                'recommendations': _get_recommendations(ml_risk_score)
            },
            'llm_analysis': llm_analysis,
            'combined_risk_score': _combine_risk_scores(ml_risk_score, llm_analysis['risk_assessment']['overall_risk_score']),
            'confidence_score': _calculate_confidence_score(ml_risk_score, llm_analysis['risk_assessment']['confidence_score'])
        }
        
        return jsonify(combined_analysis)
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            'error': 'Error processing request',
            'details': str(e)
        }), 500

@app.route('/api/ai/analyze/document', methods=['POST'])
def analyze_specific_document():
    """
    Analyze a specific tax document for risk assessment
    """
    try:
        document = request.json.get('document')
        risk_type = request.json.get('risk_type', 'general')
        
        if not document:
            return jsonify({'error': 'No document provided'}), 400
        
        analysis = llm_analyzer.analyze_specific_risk(document, risk_type)
        return jsonify(analysis)
    
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        return jsonify({
            'error': 'Error analyzing document',
            'details': str(e)
        }), 500

def _get_risk_level(risk_score: float) -> str:
    """Convert numerical risk score to risk level"""
    if risk_score < 0.2:
        return "Very Low"
    elif risk_score < 0.4:
        return "Low"
    elif risk_score < 0.6:
        return "Medium"
    elif risk_score < 0.8:
        return "High"
    else:
        return "Very High"

def _get_risk_factors(tax_data: dict, risk_score: float) -> list:
    """Identify specific factors contributing to audit risk"""
    risk_factors = []
    
    # Check income-related factors
    if tax_data.get('total_income', 0) > 200000:
        risk_factors.append("High income level")
    
    if len(tax_data.get('income_sources', [])) > 3:
        risk_factors.append("Multiple income sources")
    
    # Check deduction-related factors
    if tax_data.get('total_deductions', 0) / tax_data.get('total_income', 1) > 0.5:
        risk_factors.append("High deduction-to-income ratio")
    
    # Check business-related factors
    if tax_data.get('business_expenses', 0) / tax_data.get('business_income', 1) > 0.8:
        risk_factors.append("High business expense ratio")
    
    # Check red flag factors
    if tax_data.get('home_office_deduction', 0) > 10000:
        risk_factors.append("Large home office deduction")
    
    if tax_data.get('vehicle_expenses', 0) > 10000:
        risk_factors.append("High vehicle expenses")
    
    return risk_factors

def _get_recommendations(risk_score: float) -> list:
    """Generate recommendations based on risk score"""
    recommendations = []
    
    if risk_score > 0.6:
        recommendations.extend([
            "Consider consulting with a tax professional",
            "Ensure all deductions are well-documented",
            "Review business expense documentation",
            "Double-check all income sources are reported"
        ])
    elif risk_score > 0.4:
        recommendations.extend([
            "Review deduction documentation",
            "Ensure all income is properly reported",
            "Keep detailed records of all transactions"
        ])
    else:
        recommendations.extend([
            "Continue maintaining good record-keeping practices",
            "Stay updated on tax law changes"
        ])
    
    return recommendations

def _combine_risk_scores(ml_score: float, llm_score: float) -> float:
    """Combine ML and LLM risk scores with weighted average"""
    ml_weight = 0.6  # Give more weight to ML model
    llm_weight = 0.4
    return (ml_score * ml_weight) + (llm_score * llm_weight)

def _calculate_confidence_score(ml_score: float, llm_confidence: float) -> float:
    """Calculate overall confidence score"""
    ml_confidence = 0.8  # Base confidence in ML model
    return (ml_confidence * 0.7) + (llm_confidence * 0.3)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 