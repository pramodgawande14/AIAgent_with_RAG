# Quick Start Guide

Get your AI RAG chatbot running in 5 minutes!

## 1. Setup Environment (2 minutes)

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Configure API Key (1 minute)

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
# For OpenAI:
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-3.5-turbo

# For Anthropic Claude:
# ANTHROPIC_API_KEY=your-key-here
# LLM_MODEL=claude-3-haiku-20240307
```

## 3. Add PDF Documents (1 minute)

```bash
# Copy your PDFs to the data directory
cp ~/Documents/*.pdf data/pdfs/
```

## 4. Run the Application (1 minute)

```bash
# Start the server
python app.py

# Or use the convenience script
./run.sh  # Linux/Mac
run.bat   # Windows
```

## 5. Use the Chatbot!

Open your browser to: **http://localhost:5000**

### Example Questions:

1. "What are the main topics in these documents?"
2. "Summarize the key points from the research paper"
3. "What does the manual say about installation?"
4. "Compare the findings from different sources"

## Troubleshooting

### Can't find PDFs?
```bash
ls -la data/pdfs/  # Check files are there
```

### API Key Error?
- Check `.env` file has correct key
- Verify no extra spaces or quotes

### Port Already in Use?
```bash
# Change port in .env
FLASK_PORT=5001
```

## Next Steps

- Read the full [README.md](README.md) for advanced features
- Explore API endpoints for integration
- Customize the system prompt for your use case
- Add more PDF documents to expand knowledge base

## Need Help?

1. Check configuration: `cat .env`
2. Verify PDFs exist: `ls data/pdfs/`
3. Check logs in terminal output
4. Review [README.md](README.md) troubleshooting section

---

**Happy chatting! 🚀**
