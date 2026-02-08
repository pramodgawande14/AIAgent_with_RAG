"""Flask application for AI RAG Chatbot."""
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

from src.utils.config import Config
from src.utils.session_manager import SessionManager
from src.llm.litellm_client import LiteLLMClient
from src.rag.pdf_processor import PDFProcessor
from src.rag.vector_store import VectorStore
from src.rag.retriever import Retriever
from src.agents.base_agent import BaseAgent

# Initialize Flask app
app = Flask(__name__, 
            template_folder='ui/templates',
            static_folder='ui/static')
app.secret_key = Config.SECRET_KEY
CORS(app)

# Global variables for components
agent = None
vector_store = None

def initialize_rag_system():
    """Initialize the RAG system with PDF documents."""
    global vector_store
    
    print("Initializing RAG system...")
    
    # Ensure directories exist
    Config.ensure_directories()
    
    # Initialize PDF processor
    pdf_processor = PDFProcessor(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP
    )
    
    # Initialize vector store
    vector_store = VectorStore(
        persist_directory=str(Config.CHROMA_DIR),
        collection_name="pdf_documents",
        embedding_model=Config.EMBEDDING_MODEL
    )
    
    # Check if we need to index PDFs
    stats = vector_store.get_collection_stats()
    print(f"Current vector store: {stats['document_count']} documents")
    
    # Process PDFs if directory is not empty
    pdf_files = list(Config.PDF_DIR.glob("*.pdf"))
    if pdf_files:
        print(f"Found {len(pdf_files)} PDF files")
        
        # Ask if we should reindex (in production, you might want to automate this)
        if stats['document_count'] == 0:
            print("Indexing PDFs for the first time...")
            documents = pdf_processor.process_directory(str(Config.PDF_DIR))
            vector_store.add_documents(documents)
        else:
            print("Using existing vector store index")
    else:
        print(f"Warning: No PDF files found in {Config.PDF_DIR}")
    
    print("RAG system initialized successfully")

def initialize_agent():
    """Initialize the AI agent."""
    global agent, vector_store
    
    print("Initializing AI agent...")
    
    # Initialize LLM client
    llm_client = LiteLLMClient(
        model=Config.LLM_MODEL,
        temperature=0.7
    )
    
    # Initialize retriever
    retriever = Retriever(
        vector_store=vector_store,
        top_k=Config.TOP_K_RESULTS
    )
    
    # Initialize agent
    agent = BaseAgent(
        llm_client=llm_client,
        retriever=retriever,
        session_timeout=Config.SESSION_TIMEOUT,
        max_chat_history=Config.MAX_CHAT_HISTORY
    )
    
    print("AI agent initialized successfully")

# Routes
@app.route('/')
def index():
    """Render the main chat interface."""
    return render_template('index.html')

@app.route('/api/session/create', methods=['POST'])
def create_session():
    """Create a new chat session."""
    try:
        session_id = agent.create_session()
        return jsonify({
            'session_id': session_id,
            'success': True
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/session/clear', methods=['POST'])
def clear_session():
    """Clear chat history for a session."""
    try:
        data = request.json
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'Session ID required'}), 400
        
        agent.clear_session_history(session_id)
        
        return jsonify({
            'success': True,
            'message': 'Chat history cleared'
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process a chat message."""
    try:
        data = request.json
        session_id = data.get('session_id')
        query = data.get('query')
        use_rag = data.get('use_rag', True)
        
        if not session_id or not query:
            return jsonify({'error': 'Session ID and query required'}), 400
        
        # Process query through agent
        result = agent.process_query(
            session_id=session_id,
            query=query,
            use_rag=use_rag,
            top_k=Config.TOP_K_RESULTS
        )
        
        return jsonify({
            'response': result['response'],
            'sources': result['sources'],
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/history/<session_id>', methods=['GET'])
def get_history(session_id):
    """Get chat history for a session."""
    try:
        history = agent.get_session_history(session_id)
        return jsonify({
            'history': history,
            'success': True
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics."""
    try:
        active_sessions = agent.get_active_sessions_count()
        vector_stats = vector_store.get_collection_stats()
        
        return jsonify({
            'active_sessions': active_sessions,
            'indexed_documents': vector_stats['document_count'],
            'success': True
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/reindex', methods=['POST'])
def reindex_pdfs():
    """Reindex all PDF files."""
    try:
        print("Starting reindexing process...")
        
        # Clear existing index
        vector_store.clear_and_reload()
        
        # Process PDFs
        pdf_processor = PDFProcessor(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        
        documents = pdf_processor.process_directory(str(Config.PDF_DIR))
        vector_store.add_documents(documents)
        
        stats = vector_store.get_collection_stats()
        
        return jsonify({
            'success': True,
            'message': 'Reindexing complete',
            'documents_indexed': stats['document_count']
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

if __name__ == '__main__':
    try:
        # Validate configuration
        Config.validate()
        
        # Initialize RAG system
        initialize_rag_system()
        
        # Initialize agent
        initialize_agent()
        
        # Run Flask app
        print(f"\n{'='*60}")
        print(f"AI RAG Chatbot is running!")
        print(f"Access the UI at: http://localhost:{Config.PORT}")
        print(f"{'='*60}\n")
        
        app.run(
            host='0.0.0.0',
            port=Config.PORT,
            debug=Config.DEBUG
        )
        
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        print("\nPlease check your configuration in .env file")
