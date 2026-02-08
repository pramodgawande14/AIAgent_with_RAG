# Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                     (Flask + HTML/CSS/JS)                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ HTTP/REST API
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      Flask Application                       │
│                         (app.py)                             │
└───────────────────────────┬─────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
┌───────────▼──────┐ ┌──────▼──────┐ ┌─────▼────────┐
│   Base Agent     │ │  Session    │ │    Config    │
│  (base_agent.py) │ │  Manager    │ │  (config.py) │
└────────┬─────────┘ └─────────────┘ └──────────────┘
         │
         │ Orchestrates
         │
    ┌────┴─────────────────────────┐
    │                              │
┌───▼──────────┐         ┌─────────▼─────────┐
│   Retriever  │         │    LLM Client     │
│ (retriever.py)│        │(litellm_client.py)│
└───┬──────────┘         └───────────────────┘
    │                              │
    │                              │ API Calls
┌───▼──────────┐                   │
│ Vector Store │         ┌─────────▼─────────┐
│(vector_store.py)       │      LiteLLM      │
└───┬──────────┘         │   (100+ LLMs)     │
    │                    └───────────────────┘
    │ Embeddings                  │
    │                             │
┌───▼──────────┐         ┌────────▼──────────┐
│   ChromaDB   │         │  OpenAI/Claude/   │
│ (Persistent) │         │  Azure/Local etc. │
└──────────────┘         └───────────────────┘
         ▲
         │
         │ Indexes
         │
┌────────┴─────────┐
│  PDF Processor   │
│(pdf_processor.py)│
└────────┬─────────┘
         │
         │ Reads
         │
┌────────▼─────────┐
│   PDF Files      │
│  (data/pdfs/)    │
└──────────────────┘
```

## Component Overview

### 1. Frontend Layer (UI)

**Location**: `ui/templates/`, `ui/static/`

**Components**:
- `index.html`: Main chat interface
- `style.css`: Modern, responsive styling
- `app.js`: Frontend logic, API communication

**Responsibilities**:
- Render chat messages
- Handle user input
- Manage UI state
- Communicate with backend via REST API

### 2. Application Layer (Flask)

**Location**: `app.py`

**Responsibilities**:
- HTTP request routing
- API endpoint management
- Component initialization
- Error handling

**Key Endpoints**:
- `POST /api/session/create`: Create new session
- `POST /api/chat`: Process chat messages
- `GET /api/stats`: System statistics
- `POST /api/reindex`: Reindex PDFs

### 3. Agent Layer

**Location**: `src/agents/base_agent.py`

**Responsibilities**:
- Orchestrate RAG workflow
- Manage conversation flow
- Integrate retrieval and generation
- Handle session context

**Key Methods**:
- `create_session()`: Initialize user session
- `process_query()`: Main query processing pipeline
- `get_session_history()`: Retrieve chat history

### 4. Session Management

**Location**: `src/utils/session_manager.py`

**Responsibilities**:
- Track active sessions
- Store chat history
- Manage session timeouts
- Session cleanup

**Features**:
- In-memory session storage
- Configurable timeout
- Chat history limits
- Session context preservation

### 5. RAG Pipeline

#### 5.1 PDF Processor

**Location**: `src/rag/pdf_processor.py`

**Responsibilities**:
- Extract text from PDFs
- Split text into chunks
- Create document metadata

**Features**:
- Multiple extraction methods (PyMuPDF, PyPDF2)
- Smart chunking with overlap
- Sentence boundary awareness

#### 5.2 Vector Store

**Location**: `src/rag/vector_store.py`

**Responsibilities**:
- Generate embeddings
- Store document vectors
- Perform similarity search
- Persist data

**Technology**:
- ChromaDB for vector storage
- Sentence Transformers for embeddings
- Persistent storage on disk

#### 5.3 Retriever

**Location**: `src/rag/retriever.py`

**Responsibilities**:
- Query vector store
- Format retrieved context
- Filter by metadata
- Rank results

### 6. LLM Integration

**Location**: `src/llm/litellm_client.py`

**Responsibilities**:
- Abstract LLM provider differences
- Manage API calls
- Format prompts
- Handle streaming

**Supported Providers**:
- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude)
- Azure OpenAI
- Local models (Ollama)
- 100+ providers via LiteLLM

### 7. Configuration

**Location**: `src/utils/config.py`

**Responsibilities**:
- Load environment variables
- Validate configuration
- Provide default values
- Ensure directory structure

## Data Flow

### Query Processing Flow

```
1. User Input (Frontend)
   ↓
2. HTTP POST to /api/chat (Flask)
   ↓
3. Session Validation (SessionManager)
   ↓
4. Query Retrieval (Retriever)
   ├─→ Generate query embedding (SentenceTransformer)
   └─→ Search vector store (ChromaDB)
   ↓
5. Context Formatting (Retriever)
   ↓
6. LLM Generation (LiteLLMClient)
   ├─→ Construct prompt with context
   └─→ Call LLM API
   ↓
7. Response Processing (BaseAgent)
   ├─→ Update chat history
   └─→ Extract sources
   ↓
8. JSON Response (Flask)
   ↓
9. UI Update (Frontend)
```

### PDF Indexing Flow

```
1. Application Startup
   ↓
2. Scan PDF Directory (PDFProcessor)
   ↓
3. For Each PDF:
   ├─→ Extract text (PyMuPDF/PyPDF2)
   ├─→ Split into chunks
   └─→ Add metadata
   ↓
4. Generate Embeddings (VectorStore)
   ↓
5. Store in ChromaDB
   ↓
6. Persist to Disk
```

## Session Management

### Session Lifecycle

```
Create Session
    ↓
[Session Active]
    ├─→ User sends message
    ├─→ Add to chat history
    ├─→ Process query
    ├─→ Update last activity
    └─→ Return to Active
    ↓
Timeout or Manual End
    ↓
[Session Expired/Deleted]
```

### Session Data Structure

```python
{
    "session_id": "uuid-string",
    "created_at": timestamp,
    "last_activity": timestamp,
    "chat_history": [
        {
            "role": "user|assistant",
            "content": "message text",
            "timestamp": "ISO-8601"
        }
    ],
    "context": {
        # Additional session-specific data
    }
}
```

## Technology Stack

### Backend
- **Framework**: Flask 3.0
- **LLM Integration**: LiteLLM 1.48+
- **Vector DB**: ChromaDB 0.4+
- **Embeddings**: Sentence Transformers
- **PDF Processing**: PyMuPDF, PyPDF2

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with flexbox/grid
- **Vanilla JavaScript**: No framework dependencies

### Data Storage
- **Vector Store**: ChromaDB (persistent)
- **Session Store**: In-memory (Python dict)
- **Configuration**: Environment variables

## Security Considerations

1. **API Keys**: Stored in `.env`, never committed
2. **Input Validation**: All user inputs validated
3. **Session Isolation**: Each session is isolated
4. **CORS**: Configured for development
5. **Error Handling**: No sensitive data in error messages

## Scalability Considerations

### Current Implementation
- In-memory session storage
- Single-process Flask server
- Local vector database

### Production Recommendations
1. **Session Storage**: Redis or database
2. **Web Server**: Gunicorn/uWSGI
3. **Load Balancing**: nginx
4. **Vector Store**: Managed service or cluster
5. **Caching**: Response caching for common queries

## Performance Optimization

1. **Chunking Strategy**: Balance size vs. context
2. **Embedding Caching**: Reuse embeddings when possible
3. **Batch Processing**: Process multiple PDFs efficiently
4. **Top-K Tuning**: Optimize retrieval count
5. **Model Selection**: Choose appropriate model size

## Extension Points

1. **Additional File Types**: Add processors for DOCX, HTML, etc.
2. **Custom Embeddings**: Swap embedding models
3. **Multiple Collections**: Separate vector stores by topic
4. **User Authentication**: Add user management
5. **Advanced Retrieval**: Implement hybrid search, reranking
6. **Conversation Memory**: Enhanced context awareness
7. **Multi-turn Reasoning**: Chain-of-thought prompting

---

**Built with modularity and extensibility in mind** 🏗️
