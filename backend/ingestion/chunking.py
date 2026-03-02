"""
Text chunking with overlap
Splits text into manageable chunks with metadata
"""
from typing import List, Dict
import re
from config import settings


class TextChunker:
    def __init__(self, chunk_size: int = None, overlap: int = None):
        """
        Initialize Text Chunker
        
        Args:
            chunk_size: Target size of chunks in tokens (approx)
            overlap: Number of overlapping tokens between chunks
        """
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.overlap = overlap or settings.CHUNK_OVERLAP
    
    def _estimate_tokens(self, text: str) -> int:
        """
        Rough token estimation (1 token ≈ 4 characters)
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        return len(text) // 4
    
    def _chars_for_tokens(self, tokens: int) -> int:
        """
        Convert token count to character count
        
        Args:
            tokens: Number of tokens
            
        Returns:
            Approximate character count
        """
        return tokens * 4
    
    def chunk_text(
        self, 
        pages: List[tuple], 
        source: str
    ) -> List[Dict]:
        """
        Chunk text from pages with overlap
        
        Args:
            pages: List of (page_number, text) tuples
            source: Source filename
            
        Returns:
            List of chunk dictionaries with metadata
        """
        chunks = []
        chunk_id = 0
        
        for page_num, text in pages:
            # Clean text
            text = self._clean_text(text)
            
            if not text.strip():
                continue
            
            # Split into sentences for better boundaries
            sentences = self._split_sentences(text)
            
            current_chunk = []
            current_size = 0
            chunk_size_chars = self._chars_for_tokens(self.chunk_size)
            overlap_chars = self._chars_for_tokens(self.overlap)
            
            for sentence in sentences:
                sentence_size = len(sentence)
                
                if current_size + sentence_size > chunk_size_chars and current_chunk:
                    # Create chunk
                    chunk_text = " ".join(current_chunk)
                    chunks.append({
                        "id": f"{source}_chunk_{chunk_id}",
                        "text": chunk_text,
                        "metadata": {
                            "page": page_num,
                            "source": source,
                            "chunk_index": chunk_id
                        }
                    })
                    chunk_id += 1
                    
                    # Keep overlap
                    overlap_text = chunk_text[-overlap_chars:]
                    overlap_sentences = self._split_sentences(overlap_text)
                    current_chunk = overlap_sentences
                    current_size = len(overlap_text)
                
                current_chunk.append(sentence)
                current_size += sentence_size
            
            # Add remaining chunk
            if current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append({
                    "id": f"{source}_chunk_{chunk_id}",
                    "text": chunk_text,
                    "metadata": {
                        "page": page_num,
                        "source": source,
                        "chunk_index": chunk_id
                    }
                })
                chunk_id += 1
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        return text.strip()
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Simple sentence splitter
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]


def chunk_document(pages: List[tuple], source: str) -> List[Dict]:
    """
    Convenience function to chunk document
    
    Args:
        pages: List of (page_number, text) tuples
        source: Source filename
        
    Returns:
        List of chunks with metadata
    """
    chunker = TextChunker()
    return chunker.chunk_text(pages, source)
