"""PDF processing module for extracting and chunking text."""
import os
from pathlib import Path
from typing import List, Dict
import PyPDF2
import fitz  # PyMuPDF
from tqdm import tqdm

class PDFProcessor:
    """Process PDF files for RAG system."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize PDF processor.
        
        Args:
            chunk_size: Size of text chunks in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text_from_pdf(self, pdf_path: str, method: str = "pymupdf") -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to PDF file
            method: Extraction method ('pymupdf' or 'pypdf2')
            
        Returns:
            Extracted text content
        """
        if method == "pymupdf":
            return self._extract_with_pymupdf(pdf_path)
        else:
            return self._extract_with_pypdf2(pdf_path)
    
    def _extract_with_pymupdf(self, pdf_path: str) -> str:
        """Extract text using PyMuPDF (more accurate)."""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            raise Exception(f"Error extracting text with PyMuPDF: {str(e)}")
    
    def _extract_with_pypdf2(self, pdf_path: str) -> str:
        """Extract text using PyPDF2 (fallback method)."""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error extracting text with PyPDF2: {str(e)}")
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Get chunk
            end = start + self.chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < text_length:
                # Look for sentence ending
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > self.chunk_size * 0.5:  # At least 50% of chunk
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - self.chunk_overlap
        
        return [c for c in chunks if c]  # Remove empty chunks
    
    def process_pdf_file(self, pdf_path: str) -> List[Dict[str, str]]:
        """
        Process a single PDF file into chunks with metadata.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of dictionaries with chunk text and metadata
        """
        filename = os.path.basename(pdf_path)
        text = self.extract_text_from_pdf(pdf_path)
        chunks = self.chunk_text(text)
        
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append({
                "text": chunk,
                "metadata": {
                    "source": filename,
                    "chunk_id": i,
                    "total_chunks": len(chunks),
                    "file_path": pdf_path
                }
            })
        
        return documents
    
    def process_directory(self, directory_path: str) -> List[Dict[str, str]]:
        """
        Process all PDF files in a directory.
        
        Args:
            directory_path: Path to directory containing PDFs
            
        Returns:
            List of all document chunks with metadata
        """
        pdf_files = list(Path(directory_path).glob("*.pdf"))
        
        if not pdf_files:
            raise ValueError(f"No PDF files found in {directory_path}")
        
        all_documents = []
        
        print(f"Processing {len(pdf_files)} PDF files...")
        for pdf_file in tqdm(pdf_files):
            try:
                documents = self.process_pdf_file(str(pdf_file))
                all_documents.extend(documents)
            except Exception as e:
                print(f"Error processing {pdf_file.name}: {str(e)}")
        
        print(f"Processed {len(all_documents)} total chunks from {len(pdf_files)} files")
        return all_documents
