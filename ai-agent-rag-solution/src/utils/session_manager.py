"""Session management for the AI agent chatbot."""
import uuid
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class SessionManager:
    """Manages user sessions and chat history."""
    
    def __init__(self, timeout: int = 3600, max_history: int = 20):
        """
        Initialize session manager.
        
        Args:
            timeout: Session timeout in seconds
            max_history: Maximum number of messages to keep in history
        """
        self.sessions: Dict[str, dict] = {}
        self.timeout = timeout
        self.max_history = max_history
    
    def create_session(self) -> str:
        """Create a new session and return session ID."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "created_at": time.time(),
            "last_activity": time.time(),
            "chat_history": [],
            "context": {}
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data by ID."""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session has expired
        if time.time() - session["last_activity"] > self.timeout:
            self.delete_session(session_id)
            return None
        
        # Update last activity
        session["last_activity"] = time.time()
        return session
    
    def delete_session(self, session_id: str):
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def add_message(self, session_id: str, role: str, content: str):
        """
        Add a message to session chat history.
        
        Args:
            session_id: Session identifier
            role: Message role (user/assistant)
            content: Message content
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found or expired")
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        session["chat_history"].append(message)
        
        # Trim history if it exceeds max_history
        if len(session["chat_history"]) > self.max_history:
            session["chat_history"] = session["chat_history"][-self.max_history:]
    
    def get_chat_history(self, session_id: str) -> List[dict]:
        """Get chat history for a session."""
        session = self.get_session(session_id)
        if not session:
            return []
        return session["chat_history"]
    
    def update_context(self, session_id: str, key: str, value):
        """Update session context."""
        session = self.get_session(session_id)
        if session:
            session["context"][key] = value
    
    def get_context(self, session_id: str, key: str, default=None):
        """Get value from session context."""
        session = self.get_session(session_id)
        if not session:
            return default
        return session["context"].get(key, default)
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        current_time = time.time()
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if current_time - session["last_activity"] > self.timeout
        ]
        for sid in expired_sessions:
            self.delete_session(sid)
        return len(expired_sessions)
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions."""
        self.cleanup_expired_sessions()
        return len(self.sessions)
