"""Document retriever for RAG system."""
from typing import List, Dict, Optional

class Retriever:
    """Retrieves relevant documents for a given query."""
    
    def __init__(self, vector_store, top_k: int = 5):
        """
        Initialize retriever.
        
        Args:
            vector_store: VectorStore instance
            top_k: Number of documents to retrieve
        """
        self.vector_store = vector_store
        self.top_k = top_k
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_by_source: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: User query
            top_k: Number of results (overrides default)
            filter_by_source: Filter results by source filename
            
        Returns:
            List of retrieved documents with metadata
        """
        k = top_k if top_k is not None else self.top_k
        
        # Build metadata filter if needed
        metadata_filter = None
        if filter_by_source:
            metadata_filter = {"source": filter_by_source}
        
        # Search vector store
        results = self.vector_store.search(
            query=query,
            top_k=k,
            filter_metadata=metadata_filter
        )
        
        return results
    
    def format_context(self, results: List[Dict]) -> str:
        """
        Format retrieved documents into context string.
        
        Args:
            results: Retrieved documents
            
        Returns:
            Formatted context string
        """
        if not results:
            return "No relevant information found in the documents."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            source = result["metadata"].get("source", "Unknown")
            text = result["text"]
            
            context_parts.append(f"[Source {i}: {source}]\n{text}")
        
        return "\n\n".join(context_parts)
    
    def retrieve_and_format(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_by_source: Optional[str] = None
    ) -> tuple[List[Dict], str]:
        """
        Retrieve documents and format them as context.
        
        Args:
            query: User query
            top_k: Number of results
            filter_by_source: Filter by source filename
            
        Returns:
            Tuple of (raw results, formatted context)
        """
        results = self.retrieve(
            query=query,
            top_k=top_k,
            filter_by_source=filter_by_source
        )
        
        context = self.format_context(results)
        
        return results, context
