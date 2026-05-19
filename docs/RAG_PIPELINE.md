# Deep Dive: High-Fidelity RAG Pipeline

The RAG pipeline in this project is optimized for "Deep RAG"—where precision and grounding are more important than speed or token cost.

## 1. Structure-Aware Extraction
Standard RAG often splits text at arbitrary character limits, which breaks the logic of technical requirements.
- **Hierarchical Chunking**: Using `docling.chunking.HierarchicalChunker`, we preserve the relationship between headings and their
  paragraphs. If a requirement is under "Section 4.2", the chunk metadata knows it belongs to "Section 4.2".
- **Table Preservation**: Tables are extracted as distinct Markdown chunks. This ensures that the structure (rows/columns) remains intact,
  allowing the LLM to reason about row-column relationships (e.g., "EMD fee for Category A is X").

## 2. Hybrid Retrieval Strategy
We use a two-pronged approach to find information:
- **Vector Search (Semantic)**: Uses `BAAI/bge-small-en-v1.5`. Good for conceptual questions like "What are the security risks?".
- **Keyword Search (BM25)**: Good for finding specific identifiers, dates, or technical codes (e.g., "DSAS-AI-2084-117") that semantic 
  models might miss.

The `retrieve` method in `rag.py` fetches the top 20 from **both** and merges them.

## 3. Cross-Encoder Reranking
Retrieval is often "noisy." To fix this, we use a **Reranker** (`BAAI/bge-reranker-base`).
- The reranker looks at the *query* and the *chunk* together.
- It calculates a score from 0 to 1 representing the actual relevance.
- This step is significantly more accurate than standard vector similarity because it performs a deep cross-attention check between the 
  question and the answer.

## 4. Prompt Engineering for Grounding
The `analyzer.py` uses a strict system prompt to prevent hallucinations:
- **Mandatory Quotes**: The AI must provide a `> "Quote"` for every claim.
- **Mandatory Citations**: Every claim must be followed by `(Page X)`.
- **Negative Constraint**: If information is missing, the AI **must** say "Not explicitly mentioned" rather than guessing.

## 5. Technical Stack
- **Vector Store**: ChromaDB (In-memory, transient).
- **Embeddings**: BGE-Small (Local via HuggingFace).
- **Reranker**: BGE-Reranker (Local via SentenceTransformers).
- **LLM**: Llama-3.1-8b-instant (via Groq).
