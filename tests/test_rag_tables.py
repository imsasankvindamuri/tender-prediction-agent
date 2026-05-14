import sys
import os
from unittest.mock import MagicMock

# Mock streamlit before importing core.rag
sys.modules["streamlit"] = MagicMock()

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core.rag import TenderRAG

def test_ingest_with_tables():
    print("Starting test_ingest_with_tables...")
    rag = TenderRAG()
    
    extraction_result = {
        "success": True,
        "full_markdown": "This is some text.\nPage 1\nMore text.",
        "tables": [
            {
                "table_index": 0,
                "page": 2,
                "caption": "Test Table",
                "markdown": "| Header |\n| --- |\n| Data |"
            }
        ],
        "metadata": {
            "filename": "test.pdf"
        }
    }
    
    rag.ingest_document(extraction_result, "test_tender")
    
    # Check if vectorstore was created
    assert rag.vectorstore is not None
    
    # Retrieve and see if table is found
    # Using a query that specifically targets the table caption
    results = rag.retrieve("Test Table", k=1)
    
    print(f"Retrieved {len(results)} results.")
    for i, res in enumerate(results):
        print(f"Result {i} metadata: {res.metadata}")
        print(f"Result {i} content snippet: {res.page_content[:100]}")

    assert len(results) > 0
    
    # Find the table result (MMR might pick text first depending on embeddings, but "Test Table" should match table)
    table_results = [res for res in results if res.metadata.get("type") == "table"]
    
    if not table_results:
        # If not in top 1, try k=5
        results = rag.retrieve("Test Table", k=5)
        table_results = [res for res in results if res.metadata.get("type") == "table"]

    assert len(table_results) > 0, "Table not found in retrieval results"
    
    found_table = table_results[0]
    assert "Table Caption: Test Table" in found_table.page_content
    assert found_table.metadata["type"] == "table"
    assert found_table.metadata["page"] == 2
    assert found_table.metadata["chunk_id"] == "table_0"
    
    print("Test passed!")

if __name__ == "__main__":
    try:
        test_ingest_with_tables()
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
