import openai
from typing import Dict, Any, Optional
import logging
import os
from dotenv import load_dotenv

load_dotenv()

class ModelManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Model configurations
        self.models = {
            'gpt4': {
                'name': 'gpt-4-turbo-preview',
                'max_tokens': 4000,
                'temperature': 0.3,
                'cost_per_1k_input': 0.01,
                'cost_per_1k_output': 0.03,
                'use_case': 'complex_analysis'
            },
            'gpt35': {
                'name': 'gpt-3.5-turbo',
                'max_tokens': 4000,
                'temperature': 0.3,
                'cost_per_1k_input': 0.0005,
                'cost_per_1k_output': 0.0015,
                'use_case': 'quick_checks'
            },
            'claude3_opus': {
                'name': 'claude-3-opus-20240229',
                'max_tokens': 200000,
                'temperature': 0.3,
                'cost_per_1k_input': 0.015,
                'cost_per_1k_output': 0.075,
                'use_case': 'complex_analysis'
            },
            'claude3_sonnet': {
                'name': 'claude-3-sonnet-20240229',
                'max_tokens': 200000,
                'temperature': 0.3,
                'cost_per_1k_input': 0.003,
                'cost_per_1k_output': 0.015,
                'use_case': 'balanced_analysis'
            }
        }
        
        # Default model selection based on use case
        self.use_case_models = {
            'complex_analysis': 'gpt4',
            'quick_checks': 'gpt35',
            'balanced_analysis': 'claude3_sonnet',
            'cost_sensitive': 'gpt35'
        }

    def get_model_config(self, use_case: str = 'complex_analysis') -> Dict[str, Any]:
        """Get model configuration based on use case"""
        model_key = self.use_case_models.get(use_case, 'gpt4')
        return self.models[model_key]

    def estimate_cost(self, 
                     input_tokens: int, 
                     output_tokens: int, 
                     model_key: str = 'gpt4') -> float:
        """Estimate cost for a given number of tokens"""
        model = self.models[model_key]
        input_cost = (input_tokens / 1000) * model['cost_per_1k_input']
        output_cost = (output_tokens / 1000) * model['cost_per_1k_output']
        return input_cost + output_cost

    def get_best_model(self, 
                      complexity: str = 'high',
                      cost_sensitive: bool = False,
                      response_time: str = 'normal') -> str:
        """
        Get the best model based on requirements
        complexity: 'low', 'medium', 'high'
        response_time: 'fast', 'normal', 'slow'
        """
        if cost_sensitive:
            return 'gpt35'
        
        if complexity == 'high':
            if response_time == 'slow':
                return 'claude3_opus'
            return 'gpt4'
        
        if complexity == 'medium':
            return 'claude3_sonnet'
        
        return 'gpt35'

    def get_model_recommendation(self, 
                               task_type: str,
                               document_size: str,
                               accuracy_requirement: str) -> Dict[str, Any]:
        """
        Get model recommendation based on task requirements
        """
        recommendations = {
            'document_analysis': {
                'small': {
                    'high': 'gpt4',
                    'medium': 'claude3_sonnet',
                    'low': 'gpt35'
                },
                'medium': {
                    'high': 'claude3_opus',
                    'medium': 'gpt4',
                    'low': 'claude3_sonnet'
                },
                'large': {
                    'high': 'claude3_opus',
                    'medium': 'claude3_opus',
                    'low': 'gpt4'
                }
            },
            'risk_assessment': {
                'small': {
                    'high': 'gpt4',
                    'medium': 'claude3_sonnet',
                    'low': 'gpt35'
                },
                'medium': {
                    'high': 'gpt4',
                    'medium': 'claude3_sonnet',
                    'low': 'gpt35'
                },
                'large': {
                    'high': 'claude3_opus',
                    'medium': 'gpt4',
                    'low': 'claude3_sonnet'
                }
            },
            'quick_checks': {
                'small': {
                    'high': 'gpt35',
                    'medium': 'gpt35',
                    'low': 'gpt35'
                },
                'medium': {
                    'high': 'gpt35',
                    'medium': 'gpt35',
                    'low': 'gpt35'
                },
                'large': {
                    'high': 'claude3_sonnet',
                    'medium': 'gpt35',
                    'low': 'gpt35'
                }
            }
        }
        
        model_key = recommendations[task_type][document_size][accuracy_requirement]
        return {
            'model': model_key,
            'config': self.models[model_key],
            'estimated_cost': self.estimate_cost(1000, 500, model_key)  # Example estimation
        }

    def get_model_comparison(self) -> Dict[str, Any]:
        """Get comparison of all available models"""
        comparison = {}
        for key, model in self.models.items():
            comparison[key] = {
                'name': model['name'],
                'max_tokens': model['max_tokens'],
                'cost_per_1k_tokens': model['cost_per_1k_input'] + model['cost_per_1k_output'],
                'use_case': model['use_case'],
                'best_for': self._get_best_use_cases(key)
            }
        return comparison

    def _get_best_use_cases(self, model_key: str) -> list:
        """Get best use cases for a specific model"""
        use_cases = {
            'gpt4': [
                'Complex tax document analysis',
                'Detailed risk assessment',
                'Generating comprehensive recommendations',
                'Understanding complex tax scenarios'
            ],
            'gpt35': [
                'Quick document classification',
                'Basic risk checks',
                'Simple recommendations',
                'Cost-sensitive operations'
            ],
            'claude3_opus': [
                'Large document analysis',
                'Complex risk assessment',
                'Detailed explanations',
                'High-accuracy requirements'
            ],
            'claude3_sonnet': [
                'Balanced analysis',
                'Medium complexity tasks',
                'Cost-effective detailed analysis',
                'General tax document processing'
            ]
        }
        return use_cases.get(model_key, []) 