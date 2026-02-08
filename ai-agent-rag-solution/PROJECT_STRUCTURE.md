# AI Agent RAG Solution - Project Structure

```
ai-agent-rag-solution/
│
├── README.md                          # Project documentation
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
│
├── data/
│   └── pdfs/                         # Folder containing PDF documents for RAG
│       ├── sample_document_1.pdf
│       └── sample_document_2.pdf
│
├── src/
│   ├── __init__.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   └── base_agent.py             # Base agent with session management
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── pdf_processor.py          # PDF reading and processing
│   │   ├── vector_store.py           # Vector database operations
│   │   └── retriever.py              # Document retrieval logic
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   └── litellm_client.py         # LiteLLM integration
│   │
│   └── utils/
│       ├── __init__.py
│       ├── session_manager.py        # Session management utilities
│       └── config.py                 # Configuration settings
│
├── ui/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css             # UI styling
│   │   └── js/
│   │       └── app.js                # Frontend JavaScript
│   │
│   └── templates/
│       └── index.html                # Main UI template
│
├── app.py                            # Flask application entry point
└── run.sh                            # Shell script to run the application
```

## Description

- **data/pdfs/**: Store your PDF documents here for the RAG system to process
- **src/agents/**: AI agent implementation with session management
- **src/rag/**: RAG pipeline components for PDF processing and retrieval
- **src/llm/**: LiteLLM client for flexible LLM provider support
- **src/utils/**: Utility modules for configuration and session management
- **ui/**: Web-based user interface (HTML/CSS/JavaScript)
- **app.py**: Main Flask application serving the chatbot UI
