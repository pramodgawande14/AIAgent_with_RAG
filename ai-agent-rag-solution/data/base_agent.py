"""Base AI Agent with RAG capabilities and session management - IMPROVED VERSION."""
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
        
        self.system_prompt = """You are a helpful AI assistant that answers questions based on provided document context.

CRITICAL INSTRUCTIONS:
1. ONLY use information from the provided context to answer questions
2. If the context doesn't contain relevant information, explicitly say: "I don't find information about that in the provided documents."
3. DO NOT make up or infer information that isn't in the context
4. When answering, cite which source document the information came from
5. Be precise and accurate - quote exact information when possible
6. If the question is unclear, ask for clarification
7. Keep answers focused and relevant to the question asked

Remember: It's better to say you don't know than to provide incorrect information."""
    
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
        retrieved_docs = []
        
        if use_rag:
            retrieved_docs, context = self.retriever.retrieve_and_format(
                query=query,
                top_k=top_k
            )
            
            # Extract unique sources
            sources = list(set([
                r["metadata"].get("source", "Unknown")
                for r in retrieved_docs
            ]))
            
            # Check if we got relevant results
            if not retrieved_docs or context == "No relevant information found in the documents.":
                # No relevant context found
                response = "I don't find any relevant information about that in the provided documents. Could you rephrase your question or ask about something else that might be in the documents?"
                self.session_manager.add_message(session_id, "assistant", response)
                return {
                    "response": response,
                    "sources": [],
                    "session_id": session_id,
                    "query": query,
                    "context_found": False
                }
        
        # Get chat history (limit to recent messages for context)
        chat_history = self.session_manager.get_chat_history(session_id)
        
        # Format chat history for LLM (exclude current query, limit to last 6 messages)
        formatted_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in chat_history[-7:-1]  # Last 6 messages, excluding current query
        ]
        
        # Generate response with improved prompting
        if use_rag and context:
            response = self._generate_with_context(
                query=query,
                context=context,
                chat_history=formatted_history,
                sources=sources
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
            "query": query,
            "context_found": True
        }
    
    def _generate_with_context(
        self,
        query: str,
        context: str,
        chat_history: List[Dict],
        sources: List[str]
    ) -> str:
        """Generate response with improved context handling."""
        
        # Build the enhanced prompt
        user_message = f"""You have access to information from these documents: {', '.join(sources)}

CONTEXT FROM DOCUMENTS:
{context}

USER QUESTION: {query}

INSTRUCTIONS:
- Answer ONLY based on the context above
- If the context doesn't contain the answer, say so clearly
- Cite which document(s) you're referencing
- Be accurate and don't add information not in the context
- Keep your answer focused on the question

ANSWER:"""

        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add recent chat history for continuity
        if chat_history:
            messages.extend(chat_history)
        
        messages.append({"role": "user", "content": user_message})
        
        return self.llm_client.generate_response(messages, max_tokens=1500)
    
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
