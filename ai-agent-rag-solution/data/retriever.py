"""Document retriever for RAG system - IMPROVED VERSION."""
from typing import List, Dict, Optional

class Retriever:
    """Retrieves relevant documents for a given query with improved relevance filtering."""
    
    def __init__(self, vector_store, top_k: int = 5, relevance_threshold: float = 0.7):
        """
        Initialize retriever.
        
        Args:
            vector_store: VectorStore instance
            top_k: Number of documents to retrieve
            relevance_threshold: Minimum similarity score (0-1, lower is more similar in distance)
        """
        self.vector_store = vector_store
        self.top_k = top_k
        self.relevance_threshold = relevance_threshold
    
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
        
        # Search vector store - retrieve more than needed for filtering
        results = self.vector_store.search(
            query=query,
            top_k=k * 2,  # Get more results to filter
            filter_metadata=metadata_filter
        )
        
        # Filter by relevance threshold
        filtered_results = []
        for result in results:
            # ChromaDB uses L2 distance - lower is better
            # Normalize and filter
            distance = result.get("distance", 0)
            
            # For L2 distance, we want low scores
            # Typical range is 0-2, we'll use threshold inversely
            if distance < self.relevance_threshold or self.relevance_threshold >= 1.0:
                filtered_results.append(result)
            
            # Stop when we have enough relevant results
            if len(filtered_results) >= k:
                break
        
        return filtered_results[:k]
    
    def format_context(self, results: List[Dict], max_context_length: int = 4000) -> str:
        """
        Format retrieved documents into context string with better structure.
        
        Args:
            results: Retrieved documents
            max_context_length: Maximum characters for context
            
        Returns:
            Formatted context string
        """
        if not results:
            return "No relevant information found in the documents."
        
        context_parts = []
        total_length = 0
        
        for i, result in enumerate(results, 1):
            source = result["metadata"].get("source", "Unknown")
            text = result["text"].strip()
            chunk_id = result["metadata"].get("chunk_id", "")
            
            # Create a well-structured context entry
            entry = f"""--- Source {i}: {source} (Section {chunk_id}) ---
{text}
"""
            
            # Check if adding this would exceed max length
            if total_length + len(entry) > max_context_length and context_parts:
                break
            
            context_parts.append(entry)
            total_length += len(entry)
        
        if not context_parts:
            return "No relevant information found in the documents."
        
        return "\n".join(context_parts)
    
    def retrieve_and_format(
        self,
        query: str,
        top_k: Optional[int] = None,
        filter_by_source: Optional[str] = None,
        max_context_length: int = 4000
    ) -> tuple[List[Dict], str]:
        """
        Retrieve documents and format them as context.
        
        Args:
            query: User query
            top_k: Number of results
            filter_by_source: Filter by source filename
            max_context_length: Maximum context length
            
        Returns:
            Tuple of (raw results, formatted context)
        """
        results = self.retrieve(
            query=query,
            top_k=top_k,
            filter_by_source=filter_by_source
        )
        
        context = self.format_context(results, max_context_length)
        
        return results, context
    
    def get_relevant_sources(self, query: str, top_k: Optional[int] = None) -> List[str]:
        """
        Get list of relevant source documents for a query.
        
        Args:
            query: User query
            top_k: Number of results
            
        Returns:
            List of unique source filenames
        """
        results = self.retrieve(query=query, top_k=top_k)
        
        sources = list(set([
            result["metadata"].get("source", "Unknown")
            for result in results
        ]))
        
        return sources
