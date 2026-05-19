import sys
import os
from unittest.mock import MagicMock

# Mock streamlit before importing core.rag
sys.modules["streamlit"] = MagicMock()

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core.rag import TenderRAG

def test_high_fidelity_rag():
    print("Starting test_high_fidelity_rag...")
    rag = TenderRAG()
    
    # Mock hierarchical chunks that Docling would now produce
    extraction_result = {
        "success": True,
        "doc_chunks": [
            {
                "text": "This is a section about Eligibility. Bidders must have 5 years experience.",
                "page": 1,
                "metadata": {"headings": ["Eligibility"]}
            },
            {
                "text": "Submission deadline is 2024-12-31.",
                "page": 5,
                "metadata": {"headings": ["Important Dates"]}
            }
        ],
        "tables": [
            {
                "table_index": 0,
                "page": 10,
                "caption": "Fee Schedule",
                "markdown": "| Item | Fee |\n| --- | --- |\n| EMD | $5000 |"
            }
        ],
        "metadata": {
            "filename": "test.pdf"
        }
    }
    
    rag.ingest_document(extraction_result, "test_tender")
    
    # Test 1: Vector Search (Semantic)
    results = rag.retrieve("Who can bid?", k=1)
    print(f"Retrieval 1 (Semantic) metadata: {results[0].metadata}")
    assert results[0].metadata["type"] == "text"
    assert "Eligibility" in results[0].page_content

    # Test 2: Keyword Search (BM25)
    results = rag.retrieve("EMD $5000", k=1)
    print(f"Retrieval 2 (Keyword/Table) metadata: {results[0].metadata}")
    assert results[0].metadata["type"] == "table"
    assert "$5000" in results[0].page_content

    # Test 3: Reranking check
    # The scores should be present in metadata
    assert "rerank_score" in results[0].metadata
    print(f"Rerank Score: {results[0].metadata['rerank_score']}")

    print("High-Fidelity RAG Test Passed!")

if __name__ == "__main__":
    try:
        test_high_fidelity_rag()
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
