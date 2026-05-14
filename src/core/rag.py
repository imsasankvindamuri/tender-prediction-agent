# src/core/rag.py
import re
import streamlit as st

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


class TenderRAG:
    """Simple RAG handler for one tender at a time."""
    
    def __init__(self, persist_directory: str = "vectorstore"):
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=120,
            separators=["\n\n## ", "\n\n### ", "\n\n", "\n", ". ", " ", ""]
        )
        self.vectorstore = None

    def ingest_document(self, extraction_result: dict, tender_id: str):
        """Ingest with better page-aware chunking"""
        if not extraction_result.get("success"):
            raise ValueError("Extraction failed")

        markdown_text = extraction_result["full_markdown"]

        chunks = self.text_splitter.split_text(markdown_text)

        documents = []
        for i, chunk in enumerate(chunks):
            # Try to extract page number from chunk (heuristic)
            page_num = None
            for line in chunk.split('\n')[:10]:  # check first few lines
                if "Page" in line or "page" in line.lower():
                    # Simple heuristic - improve later if needed
                    match = re.search(r'Page\s*(\d+)', line, re.IGNORECASE)
                    if match:
                        page_num = match.group(1)
                        break

            documents.append({
                "page_content": chunk,
                "metadata": {
                    "tender_id": tender_id,
                    "chunk_id": i,
                    "source": extraction_result["metadata"].get("filename", "unknown"),
                    "page": page_num or "N/A"
                }
            })

        self.vectorstore = Chroma.from_texts(
            texts=[doc["page_content"] for doc in documents],
            embedding=self.embeddings,
            metadatas=[doc["metadata"] for doc in documents],
            collection_name=f"tender_{tender_id}",
            persist_directory=self.persist_directory
        )

        st.success(f"✓ Ingested {len(chunks)} chunks")

    def retrieve(self, query: str, k: int = 6) -> list:
        """Retrieve most relevant chunks for a query"""
        if self.vectorstore is None:
            raise ValueError("No vectorstore loaded. Ingest a document first.")
        
        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": k}
        )
        return retriever.invoke(query)
