import pytest
from pathlib import Path
from ..src.document_processor import DocumentProcessor
from ..src.tax_analyzer import TaxAnalyzer

def test_process_text_file(sample_w2_file, sample_1099_file):
    processor = DocumentProcessor()
    analyzer = TaxAnalyzer()
    
    # Process W-2 file
    w2_result = processor.process_file(sample_w2_file)
    assert w2_result['success'] is True
    assert w2_result['type'] == 'text'
    assert len(w2_result['text']) > 0
    
    # Analyze W-2
    w2_analysis = analyzer.analyze_document('w2', w2_result['text'])
    assert w2_analysis['success'] is True
    assert w2_analysis['type'] == 'w2'
    
    # Process 1099 file
    form1099_result = processor.process_file(sample_1099_file)
    assert form1099_result['success'] is True
    assert form1099_result['type'] == 'text'
    assert len(form1099_result['text']) > 0
    
    # Analyze 1099
    form1099_analysis = analyzer.analyze_document('1099', form1099_result['text'])
    assert form1099_analysis['success'] is True
    assert form1099_analysis['type'] == '1099'

def test_process_invalid_file(temp_dir):
    processor = DocumentProcessor()
    
    # Create an invalid file
    invalid_file = temp_dir / "invalid.txt"
    invalid_file.write_text("Invalid content")
    
    # Try to process invalid file
    result = processor.process_file(invalid_file)
    assert result['success'] is False
    assert 'error' in result

def test_process_file_not_found():
    processor = DocumentProcessor()
    
    # Try to process non-existent file
    result = processor.process_file(Path("nonexistent.txt"))
    assert result['success'] is False
    assert 'error' in result

def test_process_multiple_pages(temp_dir):
    processor = DocumentProcessor()
    analyzer = TaxAnalyzer()
    
    # Create a multi-page text file
    multi_page_file = temp_dir / "multi_page.txt"
    content = """
Page 1:
Form W-2 Wage and Tax Statement 2023
Employer's name: ACME Corporation
Employer's EIN: 12-3456789
Employee's SSN: 123-45-6789
Employee's name: John Doe
Employee's address: 123 Main St, Anytown, USA
Wages, tips, other compensation: 50,000.00
Federal income tax withheld: 8,000.00

Page 2:
Social security wages: 50,000.00
Social security tax withheld: 3,100.00
Medicare wages and tips: 50,000.00
Medicare tax withheld: 725.00
State: CA
State income tax: 2,500.00
State wages, tips, etc: 50,000.00
"""
    multi_page_file.write_text(content)
    
    # Process multi-page file
    result = processor.process_file(multi_page_file)
    assert result['success'] is True
    assert result['type'] == 'text'
    assert len(result['text']) > 0
    
    # Analyze the combined text
    analysis = analyzer.analyze_document('w2', result['text'])
    assert analysis['success'] is True
    assert analysis['type'] == 'w2'
    
    # Verify all data was extracted
    data = analysis['data']
    assert data['employer_name'] == 'ACME Corporation'
    assert data['employer_ein'] == '12-3456789'
    assert data['employee_ssn'] == '123-45-6789'
    assert data['wages'] == '50,000.00'
    assert data['federal_tax_withheld'] == '8,000.00'
    
    totals = analysis['totals']
    assert totals['total_wages'] == 50000.0
    assert totals['total_taxes_withheld'] == 14325.0 