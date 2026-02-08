"""Flask application for AI RAG Chatbot - IMPROVED VERSION."""
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
    
    print("\n" + "="*60)
    print("Initializing RAG system...")
    print("="*60)
    
    # Ensure directories exist
    Config.ensure_directories()
    
    # Initialize PDF processor with optimized settings
    pdf_processor = PDFProcessor(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP
    )
    
    # Initialize vector store
    print(f"Loading embedding model: {Config.EMBEDDING_MODEL}")
    vector_store = VectorStore(
        persist_directory=str(Config.CHROMA_DIR),
        collection_name="pdf_documents",
        embedding_model=Config.EMBEDDING_MODEL
    )
    
    # Check if we need to index PDFs
    stats = vector_store.get_collection_stats()
    print(f"Current vector store: {stats['document_count']} chunks indexed")
    
    # Process PDFs if directory is not empty
    pdf_files = list(Config.PDF_DIR.glob("*.pdf"))
    if pdf_files:
        print(f"Found {len(pdf_files)} PDF files")
        
        # Index if empty or force reindex
        if stats['document_count'] == 0:
            print("\n📚 Indexing PDFs for the first time...")
            documents = pdf_processor.process_directory(str(Config.PDF_DIR))
            if documents:
                vector_store.add_documents(documents)
                print(f"✅ Successfully indexed {len(documents)} chunks")
            else:
                print("⚠️ No documents were extracted from PDFs")
        else:
            print("✅ Using existing vector store index")
            print(f"   To reindex, use POST /api/reindex endpoint")
    else:
        print(f"\n⚠️ Warning: No PDF files found in {Config.PDF_DIR}")
        print(f"   Please add PDF files to start using the chatbot")
    
    print("="*60)
    print("RAG system initialized")
    print("="*60 + "\n")

def initialize_agent():
    """Initialize the AI agent with improved settings."""
    global agent, vector_store
    
    print("Initializing AI agent...")
    
    # Initialize LLM client with lower temperature for accuracy
    llm_client = LiteLLMClient(
        model=Config.LLM_MODEL,
        temperature=Config.LLM_TEMPERATURE  # Lower temperature for factual responses
    )
    
    # Initialize retriever with relevance filtering
    retriever = Retriever(
        vector_store=vector_store,
        top_k=Config.TOP_K_RESULTS,
        relevance_threshold=Config.RELEVANCE_THRESHOLD
    )
    
    # Initialize agent
    agent = BaseAgent(
        llm_client=llm_client,
        retriever=retriever,
        session_timeout=Config.SESSION_TIMEOUT,
        max_chat_history=Config.MAX_CHAT_HISTORY
    )
    
    print(f"✅ AI agent initialized")
    print(f"   Model: {Config.LLM_MODEL}")
    print(f"   Temperature: {Config.LLM_TEMPERATURE}")
    print(f"   Top-K retrieval: {Config.TOP_K_RESULTS}")
    print(f"   Chunk size: {Config.CHUNK_SIZE}")
    print()

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
        print(f"Error creating session: {str(e)}")
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
        print(f"Error clearing session: {str(e)}")
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
        
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"Use RAG: {use_rag}")
        
        # Process query through agent
        result = agent.process_query(
            session_id=session_id,
            query=query,
            use_rag=use_rag,
            top_k=Config.TOP_K_RESULTS
        )
        
        print(f"Sources: {result['sources']}")
        print(f"Context found: {result.get('context_found', True)}")
        print(f"{'='*60}\n")
        
        return jsonify({
            'response': result['response'],
            'sources': result['sources'],
            'success': True
        })
        
    except Exception as e:
        print(f"Error processing chat: {str(e)}")
        import traceback
        traceback.print_exc()
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
        print(f"Error getting history: {str(e)}")
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
            'config': {
                'model': Config.LLM_MODEL,
                'temperature': Config.LLM_TEMPERATURE,
                'chunk_size': Config.CHUNK_SIZE,
                'top_k': Config.TOP_K_RESULTS
            },
            'success': True
        })
    except Exception as e:
        print(f"Error getting stats: {str(e)}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/reindex', methods=['POST'])
def reindex_pdfs():
    """Reindex all PDF files."""
    try:
        print("\n" + "="*60)
        print("Starting reindexing process...")
        print("="*60)
        
        # Clear existing index
        vector_store.clear_and_reload()
        
        # Process PDFs
        pdf_processor = PDFProcessor(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        
        documents = pdf_processor.process_directory(str(Config.PDF_DIR))
        
        if documents:
            vector_store.add_documents(documents)
            stats = vector_store.get_collection_stats()
            
            print("="*60)
            print(f"✅ Reindexing complete: {stats['document_count']} chunks")
            print("="*60 + "\n")
            
            return jsonify({
                'success': True,
                'message': 'Reindexing complete',
                'documents_indexed': stats['document_count']
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No documents found to index'
            }), 400
        
    except Exception as e:
        print(f"Error reindexing: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

if __name__ == '__main__':
    try:
        print("\n" + "="*60)
        print("🤖 AI RAG Chatbot - Starting Up")
        print("="*60 + "\n")
        
        # Validate configuration
        Config.validate()
        print("✅ Configuration validated")
        
        # Initialize RAG system
        initialize_rag_system()
        
        # Initialize agent
        initialize_agent()
        
        # Run Flask app
        print("="*60)
        print("🚀 AI RAG Chatbot is running!")
        print(f"📱 Access the UI at: http://localhost:{Config.PORT}")
        print(f"📊 Model: {Config.LLM_MODEL}")
        print(f"🔧 Temperature: {Config.LLM_TEMPERATURE} (lower = more accurate)")
        print("="*60 + "\n")
        
        app.run(
            host='0.0.0.0',
            port=Config.PORT,
            debug=Config.DEBUG
        )
        
    except Exception as e:
        print(f"\n❌ Error starting application: {str(e)}")
        print("\nPlease check:")
        print("1. .env file exists with your API key")
        print("2. PDF files are in data/pdfs/ directory")
        print("3. All dependencies are installed")
        import traceback
        traceback.print_exc()
