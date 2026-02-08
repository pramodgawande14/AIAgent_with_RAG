"""Base AI Agent with RAG capabilities and session management."""
from typing import Optional, Dict, List
from ..utils.session_manager import SessionManager
from ..rag.retriever import Retriever
from ..llm.litellm_client import LiteLLMClient

class BaseAgent:
    """Base AI Agent with RAG and session management."""
    
    def __init__(
        self,
        llm_client: LiteLLMClient,
        retriever: Retriever,
        session_timeout: int = 3600,
        max_chat_history: int = 20
    ):
        """
        Initialize base agent.
        
        Args:
            llm_client: LiteLLM client instance
            retriever: Document retriever instance
            session_timeout: Session timeout in seconds
            max_chat_history: Maximum messages to keep in history
        """
        self.llm_client = llm_client
        self.retriever = retriever
        self.session_manager = SessionManager(
            timeout=session_timeout,
            max_history=max_chat_history
        )
        
        self.system_prompt = """You are a helpful AI assistant with access to document knowledge.
Your role is to answer questions based on the provided context from PDF documents.

Guidelines:
- Always prioritize information from the provided context
- If the context doesn't contain relevant information, clearly state this
- Be concise and accurate in your responses
- If asked about sources, reference the document names mentioned in the context
- Maintain a professional and helpful tone
"""
    
    def create_session(self) -> str:
        """Create a new chat session."""
        return self.session_manager.create_session()
    
    def end_session(self, session_id: str):
        """End a chat session."""
        self.session_manager.delete_session(session_id)
    
    def process_query(
        self,
        session_id: str,
        query: str,
        use_rag: bool = True,
        top_k: int = 5
    ) -> Dict:
        """
        Process a user query with RAG and session management.
        
        Args:
            session_id: Session identifier
            query: User query
            use_rag: Whether to use RAG for context retrieval
            top_k: Number of documents to retrieve
            
        Returns:
            Dictionary with response and metadata
        """
        # Validate session
        session = self.session_manager.get_session(session_id)
        if not session:
            raise ValueError(f"Invalid or expired session: {session_id}")
        
        # Add user message to history
        self.session_manager.add_message(session_id, "user", query)
        
        # Retrieve context if RAG is enabled
        context = ""
        sources = []
        
        if use_rag:
            results, context = self.retriever.retrieve_and_format(
                query=query,
                top_k=top_k
            )
            
            # Extract unique sources
            sources = list(set([
                r["metadata"].get("source", "Unknown")
                for r in results
            ]))
        
        # Get chat history
        chat_history = self.session_manager.get_chat_history(session_id)
        
        # Format chat history for LLM (exclude current query)
        formatted_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in chat_history[:-1]  # Exclude the just-added user query
        ]
        
        # Generate response
        if use_rag and context:
            response = self.llm_client.generate_with_context(
                query=query,
                context=context,
                chat_history=formatted_history,
                system_prompt=self.system_prompt
            )
        else:
            # Generate without RAG context
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(formatted_history)
            messages.append({"role": "user", "content": query})
            response = self.llm_client.generate_response(messages)
        
        # Add assistant response to history
        self.session_manager.add_message(session_id, "assistant", response)
        
        return {
            "response": response,
            "sources": sources,
            "session_id": session_id,
            "query": query
        }
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        """Get chat history for a session."""
        return self.session_manager.get_chat_history(session_id)
    
    def clear_session_history(self, session_id: str):
        """Clear chat history for a session while keeping the session active."""
        session = self.session_manager.get_session(session_id)
        if session:
            session["chat_history"] = []
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions."""
        return self.session_manager.get_active_sessions_count()
    
    def cleanup_sessions(self):
        """Clean up expired sessions."""
        return self.session_manager.cleanup_expired_sessions()
    
    def set_system_prompt(self, prompt: str):
        """Update the system prompt."""
        self.system_prompt = prompt
