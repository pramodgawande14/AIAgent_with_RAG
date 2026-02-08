# AI Agent RAG Solution with Google ADK and Python

A comprehensive AI chatbot solution implementing Retrieval-Augmented Generation (RAG) to answer questions from PDF documents. Built with Python, LiteLLM, ChromaDB, and Flask.

## 🚀 Features

- **RAG Implementation**: Extract and index content from PDF documents using vector embeddings
- **Flexible LLM Support**: Use any LLM provider via LiteLLM (OpenAI, Anthropic, Azure, local models, etc.)
- **Session Management**: Built-in session handling with chat history
- **Modern Web UI**: Clean, responsive interface for chatbot interactions
- **Vector Search**: ChromaDB for efficient semantic search
- **Multi-Document Support**: Process and query multiple PDF files simultaneously

## 📋 Prerequisites

- Python 3.8 or higher
- API key for your chosen LLM provider (OpenAI, Anthropic, etc.)
- PDF documents to index (place in `data/pdfs/` directory)

## 🛠️ Installation

### 1. Clone or Download the Project

```bash
cd ai-agent-rag-solution
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` file with your settings:

```env
# For OpenAI
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-3.5-turbo

# OR for Anthropic Claude
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
# LLM_MODEL=claude-3-haiku-20240307

# OR for local models (Ollama)
# LLM_MODEL=ollama/llama2
# OLLAMA_API_BASE=http://localhost:11434
```

### 5. Add PDF Documents

Place your PDF files in the `data/pdfs/` directory:

```bash
cp your-documents/*.pdf data/pdfs/
```

## 🎯 Usage

### Start the Application

```bash
python app.py
```

The application will:
1. Load and validate configuration
2. Index PDF documents (first run only)
3. Initialize the AI agent
4. Start the web server

Access the UI at: **http://localhost:5000**

### Using the Chatbot

1. **Ask Questions**: Type your question in the input box
2. **Get Answers**: The AI will search relevant PDF content and provide answers
3. **View Sources**: See which documents were used for the answer
4. **Session Management**: 
   - Use "Clear Chat" to reset conversation
   - Use "New Session" to start fresh with a new session ID

### Example Queries

```
"What are the main topics covered in the documents?"
"Summarize the key findings from the research paper"
"What does the manual say about installation?"
"Compare the recommendations from different documents"
```

## 📁 Project Structure

```
ai-agent-rag-solution/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
├── README.md                       # This file
│
├── data/
│   ├── pdfs/                       # PDF documents (add yours here)
│   └── chroma_db/                  # Vector database (auto-created)
│
├── src/
│   ├── agents/
│   │   └── base_agent.py          # AI agent with session management
│   ├── rag/
│   │   ├── pdf_processor.py       # PDF text extraction
│   │   ├── vector_store.py        # ChromaDB vector store
│   │   └── retriever.py           # Document retrieval
│   ├── llm/
│   │   └── litellm_client.py      # LiteLLM wrapper
│   └── utils/
│       ├── config.py               # Configuration
│       └── session_manager.py     # Session management
│
└── ui/
    ├── templates/
    │   └── index.html              # Main UI
    └── static/
        ├── css/
        │   └── style.css           # Styling
        └── js/
            └── app.js              # Frontend logic
```

## 🔧 Configuration Options

### LLM Models

LiteLLM supports 100+ LLM providers. Common examples:

```env
# OpenAI
LLM_MODEL=gpt-3.5-turbo
LLM_MODEL=gpt-4

# Anthropic
LLM_MODEL=claude-3-haiku-20240307
LLM_MODEL=claude-3-sonnet-20240229

# Azure OpenAI
LLM_MODEL=azure/gpt-35-turbo

# Local (Ollama)
LLM_MODEL=ollama/llama2
LLM_MODEL=ollama/mistral
```

### RAG Parameters

Adjust in `.env` or `src/utils/config.py`:

```python
CHUNK_SIZE=1000              # Size of text chunks
CHUNK_OVERLAP=200            # Overlap between chunks
TOP_K_RESULTS=5              # Number of documents to retrieve
```

### Session Settings

```python
SESSION_TIMEOUT=3600         # Session timeout (seconds)
MAX_CHAT_HISTORY=20          # Max messages to keep
```

## 🔌 API Endpoints

### Create Session
```bash
POST /api/session/create
Response: {"session_id": "...", "success": true}
```

### Send Chat Message
```bash
POST /api/chat
Body: {
  "session_id": "...",
  "query": "Your question",
  "use_rag": true
}
Response: {
  "response": "Answer...",
  "sources": ["doc1.pdf", "doc2.pdf"],
  "success": true
}
```

### Get Statistics
```bash
GET /api/stats
Response: {
  "active_sessions": 5,
  "indexed_documents": 1250,
  "success": true
}
```

### Reindex PDFs
```bash
POST /api/reindex
Response: {
  "success": true,
  "documents_indexed": 1250
}
```

## 🧪 Testing

### Test PDF Processing

```python
from src.rag.pdf_processor import PDFProcessor

processor = PDFProcessor()
documents = processor.process_pdf_file("data/pdfs/sample.pdf")
print(f"Extracted {len(documents)} chunks")
```

### Test Vector Store

```python
from src.rag.vector_store import VectorStore

store = VectorStore(persist_directory="./data/chroma_db")
results = store.search("What is machine learning?", top_k=3)
```

### Test Agent

```python
from src.agents.base_agent import BaseAgent

session_id = agent.create_session()
result = agent.process_query(session_id, "Explain the main concept")
print(result['response'])
```

## 🐛 Troubleshooting

### No PDF files found
- Ensure PDFs are in `data/pdfs/` directory
- Check file permissions

### API Key Error
- Verify API key in `.env` file
- Check key has proper permissions

### Vector Store Issues
- Delete `data/chroma_db/` and restart to reindex
- Check disk space availability

### Import Errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## 🚀 Advanced Features

### Custom System Prompt

```python
agent.set_system_prompt("""
You are a specialized assistant for technical documentation.
Focus on providing detailed, technical answers with code examples.
""")
```

### Filter by Document

```python
result = agent.retriever.retrieve(
    query="installation steps",
    filter_by_source="manual.pdf"
)
```

### Adjust Temperature

```python
agent.llm_client.set_temperature(0.3)  # More focused
agent.llm_client.set_temperature(0.9)  # More creative
```

## 📊 Performance Tips

1. **Chunk Size**: Smaller chunks (500-1000 chars) for precise answers
2. **Top-K**: More results (7-10) for comprehensive context
3. **Embedding Model**: Use faster models for real-time responses
4. **Caching**: ChromaDB persists data for fast subsequent loads

## 🔐 Security Considerations

- Keep API keys secure in `.env` (never commit to git)
- Use environment variables in production
- Implement rate limiting for public deployments
- Sanitize user inputs
- Use HTTPS in production

## 📝 License

This project is provided as-is for educational and development purposes.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional file format support (Word, Excel, etc.)
- Advanced retrieval strategies
- Multi-modal support (images in PDFs)
- Authentication and user management
- Conversation persistence

## 📧 Support

For issues or questions:
1. Check the troubleshooting section
2. Review configuration settings
3. Check LiteLLM documentation for provider-specific issues

## 🎓 Learn More

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

**Built with ❤️ using Python, LiteLLM, ChromaDB, and Flask**
