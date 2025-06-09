from typing import Dict, Any, Optional
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class W2Analyzer:
    def __init__(self):
        self.field_patterns = {
            'employer_ein': r'EIN:\s*(\d{2}-\d{7})',
            'employer_name': r'Employer\'s name\s*([^\n]+)',
            'employer_address': r'Employer\'s address\s*([^\n]+)',
            'employee_ssn': r'SSN:\s*(\d{3}-\d{2}-\d{4})',
            'employee_name': r'Employee\'s name\s*([^\n]+)',
            'employee_address': r'Employee\'s address\s*([^\n]+)',
            'wages': r'Box 1\s*\$?([\d,]+\.?\d*)',
            'federal_tax': r'Box 2\s*\$?([\d,]+\.?\d*)',
            'social_security_wages': r'Box 3\s*\$?([\d,]+\.?\d*)',
            'social_security_tax': r'Box 4\s*\$?([\d,]+\.?\d*)',
            'medicare_wages': r'Box 5\s*\$?([\d,]+\.?\d*)',
            'medicare_tax': r'Box 6\s*\$?([\d,]+\.?\d*)',
            'social_security_tips': r'Box 7\s*\$?([\d,]+\.?\d*)',
            'allocated_tips': r'Box 8\s*\$?([\d,]+\.?\d*)',
            'dependent_care': r'Box 10\s*\$?([\d,]+\.?\d*)',
            'nonqualified_plans': r'Box 11\s*\$?([\d,]+\.?\d*)',
            'deferrals': r'Box 12\s*([A-Z])\s*\$?([\d,]+\.?\d*)',
            'state': r'State:\s*([A-Z]{2})',
            'state_id': r'State ID number:\s*([^\n]+)',
            'state_wages': r'State wages\s*\$?([\d,]+\.?\d*)',
            'state_tax': r'State income tax\s*\$?([\d,]+\.?\d*)',
            'local': r'Local:\s*([^\n]+)',
            'local_wages': r'Local wages\s*\$?([\d,]+\.?\d*)',
            'local_tax': r'Local income tax\s*\$?([\d,]+\.?\d*)'
        }
        
        self.box12_codes = {
            'A': 'Uncollected social security or RRTA tax on tips',
            'B': 'Uncollected Medicare tax on tips',
            'C': 'Taxable cost of group-term life insurance over $50,000',
            'D': 'Elective deferrals under a section 401(k) plan',
            'E': 'Elective deferrals under a section 403(b) plan',
            'F': 'Elective deferrals under a section 408(k)(6) plan',
            'G': 'Elective deferrals and employer contributions under a section 457(b) plan',
            'H': 'Elective deferrals under a section 501(c)(18)(D) plan',
            'J': 'Nontaxable sick pay',
            'K': '20% excise tax on excess golden parachute payments',
            'L': 'Substantiated employee business expense reimbursements',
            'M': 'Uncollected social security or RRTA tax on taxable cost of group-term life insurance over $50,000',
            'N': 'Uncollected Medicare tax on taxable cost of group-term life insurance over $50,000',
            'P': 'Excludable moving expense reimbursements paid directly to member of Armed Forces',
            'Q': 'Nontaxable combat pay',
            'R': 'Employer contributions to an Archer MSA',
            'S': 'Employee salary reduction contributions under a section 408(p) SIMPLE plan',
            'T': 'Adoption benefits',
            'V': 'Income from exercise of nonstatutory stock option(s)',
            'W': 'Employer contributions to a Health Savings Account',
            'Y': 'Deferrals under a section 409A nonqualified deferred compensation plan',
            'Z': 'Income under a section 409A nonqualified deferred compensation plan',
            'AA': 'Designated Roth contributions under a section 401(k) plan',
            'BB': 'Designated Roth contributions under a section 403(b) plan',
            'DD': 'Cost of employer-sponsored health coverage',
            'EE': 'Designated Roth contributions under a governmental section 457(b) plan',
            'FF': 'Permitted benefits under a qualified small employer health reimbursement arrangement',
            'GG': 'Income from qualified equity grants under section 83(i)',
            'HH': 'Aggregate deferrals under section 83(i) elections as of the close of such calendar year'
        }

    def analyze(self, text: str, image: Any = None) -> Dict[str, Any]:
        """
        Analyze W-2 form text and extract relevant information.
        
        Args:
            text: OCR extracted text from W-2 form
            image: Optional image data for additional analysis
            
        Returns:
            Dictionary containing extracted W-2 information
        """
        try:
            # Extract basic information
            extracted_data = self._extract_fields(text)
            
            # Validate extracted data
            validation_results = self._validate_data(extracted_data)
            
            # Calculate totals
            totals = self._calculate_totals(extracted_data)
            
            # Generate insights
            insights = self._generate_insights(extracted_data, totals)
            
            return {
                'success': True,
                'type': 'w2',
                'data': extracted_data,
                'validation': validation_results,
                'totals': totals,
                'insights': insights
            }
            
        except Exception as e:
            logger.error(f"Error analyzing W-2: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_fields(self, text: str) -> Dict[str, Any]:
        """Extract fields from W-2 text using regex patterns."""
        extracted = {}
        
        for field, pattern in self.field_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if field == 'deferrals':
                    code = match.group(1)
                    amount = match.group(2)
                    if 'deferrals' not in extracted:
                        extracted['deferrals'] = []
                    extracted['deferrals'].append({
                        'code': code,
                        'description': self.box12_codes.get(code, 'Unknown'),
                        'amount': self._parse_amount(amount)
                    })
                else:
                    extracted[field] = match.group(1)
        
        return extracted
    
    def _validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted W-2 data."""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check required fields
        required_fields = ['employer_ein', 'employee_ssn', 'wages', 'federal_tax']
        for field in required_fields:
            if field not in data:
                validation['is_valid'] = False
                validation['errors'].append(f"Missing required field: {field}")
        
        # Validate SSN format
        if 'employee_ssn' in data:
            if not re.match(r'^\d{3}-\d{2}-\d{4}$', data['employee_ssn']):
                validation['is_valid'] = False
                validation['errors'].append("Invalid SSN format")
        
        # Validate EIN format
        if 'employer_ein' in data:
            if not re.match(r'^\d{2}-\d{7}$', data['employer_ein']):
                validation['is_valid'] = False
                validation['errors'].append("Invalid EIN format")
        
        # Check for potential data inconsistencies
        if 'social_security_wages' in data and 'wages' in data:
            ss_wages = self._parse_amount(data['social_security_wages'])
            wages = self._parse_amount(data['wages'])
            if ss_wages > wages:
                validation['warnings'].append("Social security wages exceed total wages")
        
        return validation
    
    def _calculate_totals(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate totals from W-2 data."""
        totals = {
            'total_wages': 0.0,
            'total_taxes': 0.0,
            'total_deferrals': 0.0
        }
        
        # Calculate wages
        if 'wages' in data:
            totals['total_wages'] = self._parse_amount(data['wages'])
        
        # Calculate taxes
        tax_fields = ['federal_tax', 'social_security_tax', 'medicare_tax', 'state_tax', 'local_tax']
        for field in tax_fields:
            if field in data:
                totals['total_taxes'] += self._parse_amount(data[field])
        
        # Calculate deferrals
        if 'deferrals' in data:
            for deferral in data['deferrals']:
                totals['total_deferrals'] += deferral['amount']
        
        return totals
    
    def _generate_insights(self, data: Dict[str, Any], totals: Dict[str, float]) -> Dict[str, Any]:
        """Generate insights from W-2 data."""
        insights = {
            'tax_bracket': self._estimate_tax_bracket(totals['total_wages']),
            'potential_deductions': [],
            'recommendations': []
        }
        
        # Check for retirement contributions
        if 'deferrals' in data:
            retirement_codes = ['D', 'E', 'F', 'G', 'S']
            has_retirement = any(d['code'] in retirement_codes for d in data['deferrals'])
            if not has_retirement:
                insights['recommendations'].append({
                    'type': 'retirement',
                    'message': 'Consider contributing to a retirement plan to reduce taxable income',
                    'priority': 'medium'
                })
        
        # Check for health savings
        if 'deferrals' in data:
            hsa_codes = ['W']
            has_hsa = any(d['code'] in hsa_codes for d in data['deferrals'])
            if not has_hsa:
                insights['recommendations'].append({
                    'type': 'hsa',
                    'message': 'Consider contributing to an HSA for tax-free healthcare expenses',
                    'priority': 'low'
                })
        
        return insights
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float."""
        try:
            return float(amount_str.replace(',', ''))
        except (ValueError, AttributeError):
            return 0.0
    
    def _estimate_tax_bracket(self, income: float) -> str:
        """Estimate tax bracket based on income."""
        brackets = [
            (0, 11000, '10%'),
            (11001, 44725, '12%'),
            (44726, 95375, '22%'),
            (95376, 182100, '24%'),
            (182101, 231250, '32%'),
            (231251, 578125, '35%'),
            (578126, float('inf'), '37%')
        ]
        
        for lower, upper, rate in brackets:
            if lower <= income <= upper:
                return rate
        
        return 'Unknown' 