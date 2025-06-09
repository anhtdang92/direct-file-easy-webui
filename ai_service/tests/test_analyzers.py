import pytest
from ..src.analyzers.w2_analyzer import W2Analyzer
from ..src.analyzers.form1099_analyzer import Form1099Analyzer
from ..src.analyzers.analyzer_factory import AnalyzerFactory

# Sample W-2 text
SAMPLE_W2_TEXT = """
Form W-2 Wage and Tax Statement 2023
Employer's name: ACME Corporation
Employer's EIN: 12-3456789
Employee's SSN: 123-45-6789
Employee's name: John Doe
Employee's address: 123 Main St, Anytown, USA
Wages, tips, other compensation: 50,000.00
Federal income tax withheld: 8,000.00
Social security wages: 50,000.00
Social security tax withheld: 3,100.00
Medicare wages and tips: 50,000.00
Medicare tax withheld: 725.00
State: CA
State income tax: 2,500.00
State wages, tips, etc: 50,000.00
"""

# Sample 1099-NEC text
SAMPLE_1099_TEXT = """
Form 1099-NEC Non-Employee Compensation 2023
Payer's name: XYZ Consulting
Payer's TIN: 98-7654321
Payer's address: 456 Business Ave, Anytown, USA
Recipient's name: John Doe
Recipient's TIN: 123-45-6789
Recipient's address: 123 Main St, Anytown, USA
Box 1: 25,000.00
Box 4: 3,750.00
State: CA
State ID number: 1234567
State income: 1,250.00
Box 16: 1,250.00
"""

def test_w2_analyzer():
    analyzer = W2Analyzer()
    result = analyzer.analyze(SAMPLE_W2_TEXT)
    
    assert result['success'] is True
    assert result['type'] == 'w2'
    
    data = result['data']
    assert data['employer_name'] == 'ACME Corporation'
    assert data['employer_ein'] == '12-3456789'
    assert data['employee_ssn'] == '123-45-6789'
    assert data['wages'] == '50,000.00'
    assert data['federal_tax_withheld'] == '8,000.00'
    
    totals = result['totals']
    assert totals['total_wages'] == 50000.0
    assert totals['total_taxes_withheld'] == 14325.0
    
    assert len(result['insights']['tax_implications']) > 0
    assert len(result['insights']['recommendations']) > 0

def test_1099_analyzer():
    analyzer = Form1099Analyzer()
    result = analyzer.analyze(SAMPLE_1099_TEXT)
    
    assert result['success'] is True
    assert result['type'] == '1099'
    assert result['form_type'] == '1099-NEC'
    
    data = result['data']
    assert data['payer_name'] == 'XYZ Consulting'
    assert data['payer_tin'] == '98-7654321'
    assert data['recipient_tin'] == '123-45-6789'
    assert data['nonemployee_compensation'] == '25,000.00'
    assert data['federal_tax_withheld'] == '3,750.00'
    
    totals = result['totals']
    assert totals['total_income'] == 25000.0
    assert totals['total_taxes_withheld'] == 5000.0
    
    assert len(result['insights']['tax_implications']) > 0
    assert len(result['insights']['recommendations']) > 0

def test_analyzer_factory():
    factory = AnalyzerFactory()
    
    # Test getting analyzers
    w2_analyzer = factory.get_analyzer('w2')
    assert isinstance(w2_analyzer, W2Analyzer)
    
    form1099_analyzer = factory.get_analyzer('1099')
    assert isinstance(form1099_analyzer, Form1099Analyzer)
    
    # Test unsupported type
    with pytest.raises(ValueError):
        factory.get_analyzer('unsupported')
    
    # Test supported types
    supported_types = factory.get_supported_types()
    assert 'w2' in supported_types
    assert '1099' in supported_types

def test_combine_analyses():
    from ..src.tax_analyzer import TaxAnalyzer
    
    analyzer = TaxAnalyzer()
    
    # Analyze both documents
    w2_result = analyzer.analyze_document('w2', SAMPLE_W2_TEXT)
    form1099_result = analyzer.analyze_document('1099', SAMPLE_1099_TEXT)
    
    # Combine analyses
    combined = analyzer.combine_analyses([w2_result, form1099_result])
    
    assert combined['success'] is True
    assert combined['total_income'] == 75000.0  # 50,000 + 25,000
    assert combined['total_taxes_withheld'] == 19325.0  # 14,325 + 5,000
    
    assert len(combined['documents']) == 2
    assert len(combined['tax_implications']) > 0
    assert len(combined['recommendations']) > 0
    
    # Verify recommendations are sorted by priority
    priorities = [r['priority'] for r in combined['recommendations']]
    assert priorities == sorted(priorities, key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x, 3)) 