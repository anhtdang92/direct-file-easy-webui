import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from ..src.app import app
from ..src.document_processor import DocumentProcessor
from ..src.tax_analyzer import TaxAnalyzer

client = TestClient(app)

def test_empty_file_handling(temp_dir):
    processor = DocumentProcessor()
    
    # Create an empty file
    empty_file = temp_dir / "empty.txt"
    empty_file.write_text("")
    
    # Try to process empty file
    result = processor.process_file(empty_file)
    assert result['success'] is False
    assert 'error' in result

def test_large_file_handling(temp_dir):
    processor = DocumentProcessor()
    
    # Create a large file
    large_file = temp_dir / "large.txt"
    with open(large_file, 'w') as f:
        f.write('x' * (1024 * 1024 * 10))  # 10MB file
    
    # Try to process large file
    result = processor.process_file(large_file)
    assert result['success'] is False
    assert 'error' in result

def test_invalid_file_type_handling(temp_dir):
    processor = DocumentProcessor()
    
    # Create a file with invalid extension
    invalid_file = temp_dir / "invalid.xyz"
    invalid_file.write_text("Some content")
    
    # Try to process invalid file type
    result = processor.process_file(invalid_file)
    assert result['success'] is False
    assert 'error' in result

def test_malformed_w2_handling(temp_dir):
    processor = DocumentProcessor()
    analyzer = TaxAnalyzer()
    
    # Create a malformed W-2 text
    malformed_file = temp_dir / "malformed_w2.txt"
    malformed_file.write_text("""
    Form W-2
    Invalid content
    Missing required fields
    """)
    
    # Process the file
    process_result = processor.process_file(malformed_file)
    assert process_result['success'] is True
    
    # Try to analyze malformed W-2
    analysis_result = analyzer.analyze_document('w2', process_result['text'])
    assert analysis_result['success'] is False
    assert 'error' in analysis_result

def test_malformed_1099_handling(temp_dir):
    processor = DocumentProcessor()
    analyzer = TaxAnalyzer()
    
    # Create a malformed 1099 text
    malformed_file = temp_dir / "malformed_1099.txt"
    malformed_file.write_text("""
    Form 1099
    Invalid content
    Missing required fields
    """)
    
    # Process the file
    process_result = processor.process_file(malformed_file)
    assert process_result['success'] is True
    
    # Try to analyze malformed 1099
    analysis_result = analyzer.analyze_document('1099', process_result['text'])
    assert analysis_result['success'] is False
    assert 'error' in analysis_result

def test_api_error_handling():
    # Test invalid endpoint
    response = client.get("/invalid_endpoint")
    assert response.status_code == 404
    
    # Test invalid method
    response = client.get("/process")
    assert response.status_code == 405
    
    # Test missing file in upload
    response = client.post("/process")
    assert response.status_code == 422
    
    # Test invalid content type
    response = client.post(
        "/process",
        files={"file": ("test.txt", b"content", "invalid/type")}
    )
    assert response.status_code == 400

def test_analyzer_factory_error_handling():
    from ..src.analyzers.analyzer_factory import AnalyzerFactory
    
    factory = AnalyzerFactory()
    
    # Test unsupported document type
    with pytest.raises(ValueError):
        factory.get_analyzer("unsupported_type")
    
    # Test invalid analyzer registration
    with pytest.raises(TypeError):
        factory.register_analyzer("test", "not_a_class")

def test_combine_analyses_error_handling():
    analyzer = TaxAnalyzer()
    
    # Test empty analyses list
    result = analyzer.combine_analyses([])
    assert result['success'] is True
    assert result['total_income'] == 0.0
    assert result['total_taxes_withheld'] == 0.0
    
    # Test invalid analysis format
    result = analyzer.combine_analyses([{'invalid': 'format'}])
    assert result['success'] is True
    assert result['total_income'] == 0.0
    
    # Test None values in analysis
    result = analyzer.combine_analyses([None])
    assert result['success'] is False
    assert 'error' in result

def test_concurrent_processing(temp_dir):
    processor = DocumentProcessor()
    
    # Create multiple files
    files = []
    for i in range(5):
        file_path = temp_dir / f"test_{i}.txt"
        file_path.write_text(f"Test content {i}")
        files.append(file_path)
    
    # Process files concurrently
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(processor.process_file, files))
    
    # Verify all files were processed
    assert len(results) == 5
    assert all(result['success'] for result in results)

def test_memory_handling(temp_dir):
    processor = DocumentProcessor()
    
    # Create a file with repeated content
    large_file = temp_dir / "repeated.txt"
    content = "Test content " * 100000  # Large repeated content
    large_file.write_text(content)
    
    # Process the file
    result = processor.process_file(large_file)
    assert result['success'] is True
    
    # Verify memory usage didn't grow excessively
    import psutil
    process = psutil.Process()
    memory_info = process.memory_info()
    assert memory_info.rss < 1024 * 1024 * 100  # Less than 100MB 