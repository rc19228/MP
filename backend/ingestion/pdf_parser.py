"""
PDF Parser with OCR fallback
Extracts text from PDFs using pypdf, falls back to OCR if needed
"""
import io
from typing import List, Tuple
from pathlib import Path
import pypdf
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
from config import settings


class PDFParser:
    def __init__(self, ocr_threshold: int = None):
        """
        Initialize PDF Parser
        
        Args:
            ocr_threshold: Minimum character count threshold before OCR fallback
        """
        self.ocr_threshold = ocr_threshold or settings.OCR_THRESHOLD
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Tuple[int, str]]:
        """
        Extract text from PDF with OCR fallback
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of tuples: (page_number, text_content)
        """
        with open(pdf_path, 'rb') as file:
            pdf_bytes = file.read()
        
        # Try pypdf first
        pages = self._extract_with_pypdf(pdf_bytes)
        
        # Check if OCR is needed
        total_chars = sum(len(text) for _, text in pages)
        
        if total_chars < self.ocr_threshold:
            print(f"Text extraction yielded {total_chars} chars. Using OCR fallback...")
            pages = self._extract_with_ocr(pdf_bytes)
        
        return pages
    
    def _extract_with_pypdf(self, pdf_bytes: bytes) -> List[Tuple[int, str]]:
        """
        Extract text using pypdf
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            List of (page_number, text) tuples
        """
        pages = []
        pdf_file = io.BytesIO(pdf_bytes)
        reader = pypdf.PdfReader(pdf_file)
        
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            pages.append((page_num, text))
        
        return pages
    
    def _extract_with_ocr(self, pdf_bytes: bytes) -> List[Tuple[int, str]]:
        """
        Extract text using OCR (pdf2image + pytesseract)
        
        Args:
            pdf_bytes: PDF file as bytes
            
        Returns:
            List of (page_number, text) tuples
        """
        pages = []
        
        # Convert PDF to images
        images = convert_from_bytes(pdf_bytes)
        
        for page_num, image in enumerate(images, start=1):
            # Perform OCR
            text = pytesseract.image_to_string(image)
            pages.append((page_num, text))
        
        return pages


def extract_pdf(pdf_path: str) -> List[Tuple[int, str]]:
    """
    Convenience function to extract text from PDF
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        List of (page_number, text) tuples
    """
    parser = PDFParser()
    return parser.extract_text_from_pdf(pdf_path)
