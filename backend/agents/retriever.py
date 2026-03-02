"""
Retriever Agent
Retrieves relevant document chunks from ChromaDB
"""
from typing import Dict, List, Optional
from db.chroma_client import get_chroma_client
from config import settings


class RetrieverAgent:
    def __init__(self):
        """
        Initialize Retriever Agent
        """
        self.chroma = get_chroma_client()
    
    def retrieve(
        self,
        query: str,
        top_k: int = None,
        required_sections: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Retrieve relevant chunks from ChromaDB
        
        Args:
            query: User query or search text
            top_k: Number of chunks to retrieve
            required_sections: Optional filter for specific sections
            
        Returns:
            List of retrieved chunks with metadata and similarity scores
        """
        top_k = top_k or settings.TOP_K_CHUNKS
        
        # Build metadata filter if needed
        where_filter = None
        if required_sections:
            # Filter by source if specified
            where_filter = {"source": {"$in": required_sections}}
        
        # Query ChromaDB
        results = self.chroma.query(
            query_text=query,
            n_results=top_k,
            where=where_filter
        )
        
        # Format results
        retrieved_chunks = []
        
        for i in range(len(results["ids"])):
            chunk = {
                "id": results["ids"][i],
                "text": results["documents"][i],
                "metadata": results["metadatas"][i],
                "similarity_score": self._distance_to_similarity(results["distances"][i])
            }
            retrieved_chunks.append(chunk)
        
        return retrieved_chunks
    
    def _distance_to_similarity(self, distance: float) -> float:
        """
        Convert distance to similarity score (0-1)
        
        Args:
            distance: Distance metric from ChromaDB
            
        Returns:
            Similarity score between 0 and 1
        """
        # ChromaDB typically uses L2 distance
        # Convert to similarity: smaller distance = higher similarity
        similarity = 1 / (1 + distance)
        return round(similarity, 4)
    
    def get_context_text(self, chunks: List[Dict]) -> str:
        """
        Combine retrieved chunks into context text
        
        Args:
            chunks: List of retrieved chunks
            
        Returns:
            Combined context text
        """
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk["metadata"]
            text = chunk["text"]
            
            context_parts.append(
                f"[Chunk {i} - Page {metadata.get('page', 'N/A')} - "
                f"Source: {metadata.get('source', 'N/A')}]\n{text}\n"
            )
        
        return "\n".join(context_parts)


def retrieve_context(
    query: str,
    top_k: int = None,
    required_sections: Optional[List[str]] = None
) -> tuple:
    """
    Convenience function to retrieve context
    
    Args:
        query: User query
        top_k: Number of chunks to retrieve
        required_sections: Optional filter for sections
        
    Returns:
        Tuple of (chunks list, context text)
    """
    retriever = RetrieverAgent()
    chunks = retriever.retrieve(query, top_k, required_sections)
    context_text = retriever.get_context_text(chunks)
    return chunks, context_text
