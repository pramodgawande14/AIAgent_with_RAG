#!/bin/bash

# AI Agent RAG Solution - Startup Script

echo "=========================================="
echo "AI Agent RAG Solution"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Checking dependencies..."
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found!"
    echo "Copying .env.example to .env..."
    cp .env.example .env
    echo ""
    echo "Please edit .env file with your API keys before running."
    echo "Then run this script again."
    exit 1
fi

# Check if PDFs directory has files
PDF_COUNT=$(ls -1 data/pdfs/*.pdf 2>/dev/null | wc -l)
if [ $PDF_COUNT -eq 0 ]; then
    echo "Warning: No PDF files found in data/pdfs/"
    echo "Please add PDF files to data/pdfs/ directory"
    echo ""
fi

# Start the application
echo "Starting AI Agent RAG Solution..."
echo ""
python app.py
