from typing import Dict, Any, Optional
import os
import logging
from pathlib import Path
import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, temp_dir: str = "temp"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
        
    def process_document(self, file_path: str, doc_type: str) -> Dict[str, Any]:
        """
        Process a tax document and extract relevant information.
        
        Args:
            file_path: Path to the document file
            doc_type: Type of document (w2, 1099, etc.)
            
        Returns:
            Dict containing extracted information
        """
        try:
            # Convert PDF to images if needed
            if file_path.lower().endswith('.pdf'):
                images = self._convert_pdf_to_images(file_path)
            else:
                images = [Image.open(file_path)]
            
            # Process each page
            results = []
            for idx, image in enumerate(images):
                # Preprocess image
                processed_image = self._preprocess_image(image)
                
                # Extract text
                text = self._extract_text(processed_image)
                
                # Extract structured data based on document type
                if doc_type.lower() == 'w2':
                    data = self._extract_w2_data(text, processed_image)
                elif doc_type.lower() == '1099':
                    data = self._extract_1099_data(text, processed_image)
                else:
                    data = self._extract_generic_data(text, processed_image)
                
                results.append({
                    'page': idx + 1,
                    'text': text,
                    'data': data
                })
            
            # Clean up temporary files
            self._cleanup()
            
            return {
                'success': True,
                'pages': len(results),
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _convert_pdf_to_images(self, pdf_path: str) -> list:
        """Convert PDF to list of PIL Images."""
        return convert_from_path(pdf_path)
    
    def _preprocess_image(self, image: Image.Image) -> np.ndarray:
        """Preprocess image for better OCR results."""
        # Convert to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
            
        # Apply thresholding
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(binary)
        
        return denoised
    
    def _extract_text(self, image: np.ndarray) -> str:
        """Extract text from image using OCR."""
        return pytesseract.image_to_string(image)
    
    def _extract_w2_data(self, text: str, image: np.ndarray) -> Dict[str, Any]:
        """Extract data from W-2 form."""
        # TODO: Implement W-2 specific extraction logic
        return {
            'type': 'w2',
            'raw_text': text,
            'extracted_data': {}
        }
    
    def _extract_1099_data(self, text: str, image: np.ndarray) -> Dict[str, Any]:
        """Extract data from 1099 form."""
        # TODO: Implement 1099 specific extraction logic
        return {
            'type': '1099',
            'raw_text': text,
            'extracted_data': {}
        }
    
    def _extract_generic_data(self, text: str, image: np.ndarray) -> Dict[str, Any]:
        """Extract data from generic tax document."""
        return {
            'type': 'generic',
            'raw_text': text,
            'extracted_data': {}
        }
    
    def _cleanup(self):
        """Clean up temporary files."""
        for file in self.temp_dir.glob("*"):
            try:
                file.unlink()
            except Exception as e:
                logger.warning(f"Error deleting temporary file {file}: {str(e)}") 