# Architectural Overview: Tender Analyst

This document describes the high-level architecture of the Tender Analyst system, a high-fidelity RAG application designed 
for precise analysis of complex tender documents.

## System Goals
- **Precision**: 100% grounded extraction with mandatory citations.
- **Reliability**: Deterministic hierarchical chunking and hybrid retrieval.
- **Explainability**: Clear visibility into retrieved context and reranking scores.

## Component Map

### 1. UI Layer (`src/ui/`)
- **Sidebar (`sidebar.py`)**: Handles document upload and triggers the main extraction/ingest pipeline.
- **Chat (`chat.py`)**: Provides a conversational interface for follow-up questions, utilizing the RAG pipeline for grounded 
  answers.
- **Styles (`styles.py`)**: Manages the visual appearance and branding of the Streamlit app.

### 2. Core Logic (`src/core/`)
- **Extraction (`extract.py`)**: Uses **Docling** to convert PDFs into structured data. It performs hierarchical chunking, 
  table extraction, and page number preservation.
- **RAG Pipeline (`rag.py`)**: The heart of the system. Implements Hybrid Search (Vector + BM25) and Cross-Encoder Reranking.
- **Analyzer (`analyzer.py`)**: Orchestrates multiple RAG queries to build a comprehensive structured report across five key 
  tender domains.
- **LLM Manager (`llm.py`)**: Centralizes access to the LLM (Groq/Llama-3.1).
- **Config (`config.py`)**: Stores prompts, model settings, and system parameters.

## Data Flow

1. **Upload**: User uploads a PDF.
2. **Extraction**: Docling parses the PDF into hierarchical chunks and Markdown tables.
3. **Ingestion**: Chunks are embedded and stored in Chroma (Vector) and indexed in BM25 (Keyword).
4. **Analysis**: The Analyzer runs a series of predefined queries (e.g., "Submission Deadline").
5. **Retrieval**: For each query, the RAG engine pulls the top 40 candidates (20 Vector + 20 Keyword).
6. **Reranking**: A Cross-Encoder re-scores the 40 candidates to find the absolute top 8-12.
7. **Generation**: The LLM generates a grounded report with mandatory quotes and page citations.
