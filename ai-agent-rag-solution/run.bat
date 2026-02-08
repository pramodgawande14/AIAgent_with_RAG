@echo off
REM AI Agent RAG Solution - Windows Startup Script

echo ==========================================
echo AI Agent RAG Solution
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Checking dependencies...
pip install -q -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo Warning: .env file not found!
    echo Copying .env.example to .env...
    copy .env.example .env
    echo.
    echo Please edit .env file with your API keys before running.
    echo Then run this script again.
    pause
    exit /b 1
)

REM Check if PDFs directory has files
dir /b data\pdfs\*.pdf >nul 2>&1
if errorlevel 1 (
    echo Warning: No PDF files found in data\pdfs\
    echo Please add PDF files to data\pdfs\ directory
    echo.
)

REM Start the application
echo Starting AI Agent RAG Solution...
echo.
python app.py

pause
