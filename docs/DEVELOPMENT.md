# Development and Testing Guide

This project uses `poetry` for dependency management.

## Environment Setup

1. **Install Poetry**:
   ```bash
   pip install poetry
   ```

2. **Install Dependencies**:
   ```bash
   poetry install
   ```

3. **Configure Environment**:
   Create a `.env` file in the root with your Groq API key:
   ```text
   GROQ_API_KEY=gsk_...
   ```

## Running the App
```bash
poetry run streamlit run src/app.py
```

## Testing the RAG Pipeline

Because the RAG pipeline involves heavy local models (embeddings and rerankers), we use specialized smoke tests.

### Smoke Test: High-Fidelity RAG
Validates that hierarchical chunking, hybrid search, and reranking are all working correctly.
```bash
poetry run python tests/test_rag_high_fidelity.py
```

### Manual PDF Verification
To verify extraction on a real PDF (e.g., the AEGIS sentinel tender):
```bash
poetry run python tests/test_rag_tables.py
```

## Key Maintenance Files
- `src/core/config.py`: Update the `SYSTEM_PROMPT` or `INITIAL_ANALYSIS_PROMPT` here to change the AI's reporting style.
- `src/core/rag.py`: Adjust the `weights` in `retrieve` if you want to favor Keyword search over Vector search.
- `src/core/analyzer.py`: Add or remove analysis sections by updating the `sections` list in `generate_full_analysis`.
