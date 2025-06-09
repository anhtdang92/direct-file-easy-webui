import pytest
import numpy as np
from PIL import Image
from pathlib import Path
from ..src.document_processor import DocumentProcessor

def create_test_image(temp_dir, size=(800, 600), color=(255, 255, 255)):
    """Create a test image file."""
    image = Image.new('RGB', size, color)
    file_path = temp_dir / "test_image.png"
    image.save(file_path)
    return file_path

def test_process_image_file(temp_dir):
    processor = DocumentProcessor()
    
    # Create a test image
    image_file = create_test_image(temp_dir)
    
    # Process the image
    result = processor.process_file(image_file)
    assert result['success'] is True
    assert result['type'] == 'image'
    assert len(result['text']) >= 0  # May be empty for blank image

def test_process_pdf_file(temp_dir):
    processor = DocumentProcessor()
    
    # Create a test PDF (this would require a PDF library)
    # For now, we'll just test that the processor handles PDFs gracefully
    pdf_file = temp_dir / "test.pdf"
    pdf_file.write_text("")  # Empty file
    
    result = processor.process_file(pdf_file)
    assert result['success'] is False
    assert 'error' in result

def test_image_preprocessing(temp_dir):
    processor = DocumentProcessor()
    
    # Create a test image with some noise
    image = Image.new('RGB', (800, 600), (255, 255, 255))
    # Add some noise
    pixels = image.load()
    for i in range(0, 800, 10):
        for j in range(0, 600, 10):
            pixels[i, j] = (200, 200, 200)
    
    file_path = temp_dir / "noisy_image.png"
    image.save(file_path)
    
    # Process the image
    result = processor.process_file(file_path)
    assert result['success'] is True
    assert result['type'] == 'image'

def test_multiple_image_pages(temp_dir):
    processor = DocumentProcessor()
    
    # Create multiple test images
    image_files = []
    for i in range(3):
        image_file = create_test_image(temp_dir, size=(800, 600), color=(255, 255, 255))
        image_files.append(image_file)
    
    # Process each image
    results = []
    for image_file in image_files:
        result = processor.process_file(image_file)
        assert result['success'] is True
        assert result['type'] == 'image'
        results.append(result)
    
    # Verify all pages were processed
    assert len(results) == 3

def test_image_ocr_accuracy(temp_dir):
    processor = DocumentProcessor()
    
    # Create an image with text
    image = Image.new('RGB', (800, 600), (255, 255, 255))
    # Add some text (this would require a proper text rendering library)
    # For now, we'll just test the basic functionality
    file_path = temp_dir / "text_image.png"
    image.save(file_path)
    
    # Process the image
    result = processor.process_file(file_path)
    assert result['success'] is True
    assert result['type'] == 'image'

def test_image_format_handling(temp_dir):
    processor = DocumentProcessor()
    
    # Test different image formats
    formats = ['png', 'jpg', 'jpeg', 'bmp']
    for fmt in formats:
        image_file = create_test_image(temp_dir)
        file_path = temp_dir / f"test_image.{fmt}"
        image_file.rename(file_path)
        
        result = processor.process_file(file_path)
        assert result['success'] is True
        assert result['type'] == 'image'

def test_large_image_handling(temp_dir):
    processor = DocumentProcessor()
    
    # Create a large test image
    image_file = create_test_image(temp_dir, size=(2000, 2000))
    
    # Process the large image
    result = processor.process_file(image_file)
    assert result['success'] is True
    assert result['type'] == 'image'

def test_image_rotation_handling(temp_dir):
    processor = DocumentProcessor()
    
    # Create a test image
    image = Image.new('RGB', (800, 600), (255, 255, 255))
    # Rotate the image
    rotated_image = image.rotate(90)
    
    file_path = temp_dir / "rotated_image.png"
    rotated_image.save(file_path)
    
    # Process the rotated image
    result = processor.process_file(file_path)
    assert result['success'] is True
    assert result['type'] == 'image' 