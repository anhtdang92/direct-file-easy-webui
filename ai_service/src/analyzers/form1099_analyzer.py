from typing import Dict, Any, Optional
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Form1099Analyzer:
    def __init__(self):
        self.field_patterns = {
            'payer_name': r'Payer\'s name\s*([^\n]+)',
            'payer_tin': r'Payer\'s TIN\s*(\d{2}-\d{7})',
            'payer_address': r'Payer\'s address\s*([^\n]+)',
            'recipient_name': r'Recipient\'s name\s*([^\n]+)',
            'recipient_tin': r'Recipient\'s TIN\s*(\d{3}-\d{2}-\d{4})',
            'recipient_address': r'Recipient\'s address\s*([^\n]+)',
            'nonemployee_compensation': r'Box 1\s*\$?([\d,]+\.?\d*)',
            'federal_tax_withheld': r'Box 4\s*\$?([\d,]+\.?\d*)',
            'state_tax_withheld': r'Box 16\s*\$?([\d,]+\.?\d*)',
            'state': r'State:\s*([A-Z]{2})',
            'state_id': r'State ID number:\s*([^\n]+)',
            'state_income': r'State income\s*\$?([\d,]+\.?\d*)',
            'local_tax_withheld': r'Box 18\s*\$?([\d,]+\.?\d*)',
            'local': r'Local:\s*([^\n]+)',
            'local_income': r'Local income\s*\$?([\d,]+\.?\d*)'
        }
        
        self.form_types = {
            '1099-MISC': 'Miscellaneous Income',
            '1099-NEC': 'Non-Employee Compensation',
            '1099-INT': 'Interest Income',
            '1099-DIV': 'Dividends and Distributions',
            '1099-B': 'Proceeds from Broker and Barter Exchange',
            '1099-G': 'Government Payments',
            '1099-R': 'Distributions from Pensions, Annuities, etc.',
            '1099-S': 'Proceeds from Real Estate Transactions',
            '1099-K': 'Payment Card and Third Party Network Transactions'
        }

    def analyze(self, text: str, image: Any = None) -> Dict[str, Any]:
        """
        Analyze 1099 form text and extract relevant information.
        
        Args:
            text: OCR extracted text from 1099 form
            image: Optional image data for additional analysis
            
        Returns:
            Dictionary containing extracted 1099 information
        """
        try:
            # Determine form type
            form_type = self._determine_form_type(text)
            
            # Extract basic information
            extracted_data = self._extract_fields(text)
            extracted_data['form_type'] = form_type
            
            # Validate extracted data
            validation_results = self._validate_data(extracted_data)
            
            # Calculate totals
            totals = self._calculate_totals(extracted_data)
            
            # Generate insights
            insights = self._generate_insights(extracted_data, totals)
            
            return {
                'success': True,
                'type': '1099',
                'form_type': form_type,
                'data': extracted_data,
                'validation': validation_results,
                'totals': totals,
                'insights': insights
            }
            
        except Exception as e:
            logger.error(f"Error analyzing 1099: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _determine_form_type(self, text: str) -> str:
        """Determine the type of 1099 form."""
        for form_type in self.form_types.keys():
            if form_type.lower() in text.lower():
                return form_type
        return '1099-UNKNOWN'
    
    def _extract_fields(self, text: str) -> Dict[str, Any]:
        """Extract fields from 1099 text using regex patterns."""
        extracted = {}
        
        for field, pattern in self.field_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted[field] = match.group(1)
        
        return extracted
    
    def _validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted 1099 data."""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required fields based on form type
        required_fields = ['payer_tin', 'recipient_tin']
        if data.get('form_type') in ['1099-MISC', '1099-NEC']:
            required_fields.append('nonemployee_compensation')
        
        for field in required_fields:
            if field not in data:
                validation['is_valid'] = False
                validation['errors'].append(f"Missing required field: {field}")
        
        # Validate TIN format
        if 'recipient_tin' in data:
            if not re.match(r'^\d{3}-\d{2}-\d{4}$', data['recipient_tin']):
                validation['is_valid'] = False
                validation['errors'].append("Invalid recipient TIN format")
        
        if 'payer_tin' in data:
            if not re.match(r'^\d{2}-\d{7}$', data['payer_tin']):
                validation['is_valid'] = False
                validation['errors'].append("Invalid payer TIN format")
        
        # Check for potential data inconsistencies
        if 'nonemployee_compensation' in data and 'federal_tax_withheld' in data:
            comp = self._parse_amount(data['nonemployee_compensation'])
            tax = self._parse_amount(data['federal_tax_withheld'])
            if tax > comp * 0.37:  # Maximum tax rate
                validation['warnings'].append("Federal tax withheld seems unusually high")
        
        return validation
    
    def _calculate_totals(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate totals from 1099 data."""
        totals = {
            'total_income': 0.0,
            'total_taxes_withheld': 0.0
        }
        
        # Calculate income
        income_fields = [
            'nonemployee_compensation',
            'state_income',
            'local_income'
        ]
        
        for field in income_fields:
            if field in data:
                totals['total_income'] += self._parse_amount(data[field])
        
        # Calculate taxes withheld
        tax_fields = [
            'federal_tax_withheld',
            'state_tax_withheld',
            'local_tax_withheld'
        ]
        
        for field in tax_fields:
            if field in data:
                totals['total_taxes_withheld'] += self._parse_amount(data[field])
        
        return totals
    
    def _generate_insights(self, data: Dict[str, Any], totals: Dict[str, float]) -> Dict[str, Any]:
        """Generate insights from 1099 data."""
        insights = {
            'tax_implications': [],
            'recommendations': []
        }
        
        # Check for self-employment implications
        if data.get('form_type') in ['1099-MISC', '1099-NEC']:
            if 'nonemployee_compensation' in data:
                comp = self._parse_amount(data['nonemployee_compensation'])
                if comp > 0:
                    insights['tax_implications'].append({
                        'type': 'self_employment',
                        'message': 'This income may be subject to self-employment tax',
                        'priority': 'high'
                    })
                    
                    # Calculate estimated self-employment tax
                    se_tax = comp * 0.153  # 15.3% of net earnings
                    insights['recommendations'].append({
                        'type': 'estimated_tax',
                        'message': f'Consider setting aside ${se_tax:.2f} for self-employment tax',
                        'priority': 'high'
                    })
        
        # Check for state tax implications
        if 'state' in data and 'state_income' in data:
            state_income = self._parse_amount(data['state_income'])
            if state_income > 0:
                insights['tax_implications'].append({
                    'type': 'state_tax',
                    'message': f'This income is subject to {data["state"]} state tax',
                    'priority': 'medium'
                })
        
        return insights
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float."""
        try:
            return float(amount_str.replace(',', ''))
        except (ValueError, AttributeError):
            return 0.0 