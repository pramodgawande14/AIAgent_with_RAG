"""Configuration module for AI Agent RAG solution - IMPROVED VERSION."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration with optimized RAG settings."""
    
    # Base paths
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    PDF_DIR = DATA_DIR / "pdfs"
    CHROMA_DIR = DATA_DIR / "chroma_db"
    
    # LLM Configuration
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))  # Lower for more focused answers
    
    # Embedding Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # RAG Configuration - IMPROVED DEFAULTS
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))  # Smaller chunks for precision
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))  # Good overlap
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "4"))  # Fewer, more relevant results
    RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "1.5"))  # Filter low-quality matches
    MAX_CONTEXT_LENGTH = int(os.getenv("MAX_CONTEXT_LENGTH", "3000"))  # Prevent context overflow
    
    # Session Configuration
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))
    MAX_CHAT_HISTORY = int(os.getenv("MAX_CHAT_HISTORY", "10"))  # Keep focused history
    
    # Flask Configuration
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    PORT = int(os.getenv("FLASK_PORT", "5000"))
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.PDF_DIR.mkdir(exist_ok=True)
        cls.CHROMA_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def validate(cls):
        """Validate configuration."""
        errors = []
        
        # Check if LLM API key is set
        if cls.LLM_MODEL.startswith("gpt") and not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY not set for OpenAI model")
        elif cls.LLM_MODEL.startswith("claude") and not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY not set for Anthropic model")
        
        # Check if PDF directory exists and has files
        if not cls.PDF_DIR.exists():
            errors.append(f"PDF directory does not exist: {cls.PDF_DIR}")
        elif not list(cls.PDF_DIR.glob("*.pdf")):
            print(f"Warning: No PDF files found in {cls.PDF_DIR}")
        
        if errors:
            raise ValueError("\n".join(errors))
        
        return True
    
    @classmethod
    def get_rag_params(cls) -> dict:
        """Get RAG-specific parameters as a dictionary."""
        return {
            "chunk_size": cls.CHUNK_SIZE,
            "chunk_overlap": cls.CHUNK_OVERLAP,
            "top_k": cls.TOP_K_RESULTS,
            "relevance_threshold": cls.RELEVANCE_THRESHOLD,
            "max_context_length": cls.MAX_CONTEXT_LENGTH
        }
