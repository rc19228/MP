"""
ChromaDB client for vector storage and retrieval
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
from config import settings


class ChromaClient:
    def __init__(self):
        """
        Initialize ChromaDB client with persistent storage
        """
        self.client = chromadb.Client(
            ChromaSettings(
                persist_directory=settings.CHROMA_PERSIST_DIR,
                is_persistent=True,
                anonymized_telemetry=False
            )
        )
        self.collection_name = settings.CHROMA_COLLECTION_NAME
        self._init_collection()
    
    def _init_collection(self):
        """
        Initialize or get existing collection
        """
        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name=self.collection_name
            )
            print(f"Loaded existing collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Financial documents collection"}
            )
            print(f"Created new collection: {self.collection_name}")
    
    def add_documents(self, chunks: List[Dict]) -> bool:
        """
        Add document chunks to ChromaDB
        
        Args:
            chunks: List of chunk dictionaries with id, text, and metadata
            
        Returns:
            Success status
        """
        try:
            ids = [chunk["id"] for chunk in chunks]
            documents = [chunk["text"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            print(f"Added {len(chunks)} chunks to ChromaDB")
            return True
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    def query(
        self, 
        query_text: str, 
        n_results: int = None,
        where: Optional[Dict] = None
    ) -> Dict:
        """
        Query ChromaDB for similar documents
        
        Args:
            query_text: Query string
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            Dictionary with ids, documents, metadatas, and distances
        """
        n_results = n_results or settings.TOP_K_CHUNKS
        
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where
            )
            
            # Reformat results for easier use
            formatted_results = {
                "ids": results["ids"][0] if results["ids"] else [],
                "documents": results["documents"][0] if results["documents"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                "distances": results["distances"][0] if results["distances"] else []
            }
            
            return formatted_results
        except Exception as e:
            print(f"Error querying ChromaDB: {e}")
            return {
                "ids": [],
                "documents": [],
                "metadatas": [],
                "distances": []
            }
    
    def delete_collection(self):
        """
        Delete the collection (for testing/cleanup)
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            print(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            print(f"Error deleting collection: {e}")
    
    def count_documents(self) -> int:
        """
        Get count of documents in collection
        
        Returns:
            Number of documents
        """
        try:
            return self.collection.count()
        except:
            return 0


# Singleton instance
_chroma_client = None


def get_chroma_client() -> ChromaClient:
    """
    Get or create ChromaDB client singleton
    
    Returns:
        ChromaClient instance
    """
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = ChromaClient()
    return _chroma_client
