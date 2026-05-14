import re
import streamlit as st

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


class TenderRAG:
    """Simple RAG handler for one tender at a time."""

    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1600,
            chunk_overlap=200,
            separators=[
                "\n# ",
                "\n## ",
                "\n### ",
                "\n#### ",
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )

        self.vectorstore = None

    def ingest_document(self, extraction_result: dict, tender_id: str):
        """Ingest tender into vectorstore"""

        if not extraction_result.get("success"):
            raise ValueError("Extraction failed")

        markdown_text = extraction_result["full_markdown"]

        chunks = self.text_splitter.split_text(markdown_text)

        documents = []

        for i, chunk in enumerate(chunks):

            page_num = "N/A"

            for line in chunk.split("\n")[:10]:
                match = re.search(r"Page\s*(\d+)", line, re.IGNORECASE)

                if match:
                    page_num = match.group(1)
                    break

            documents.append({
                "page_content": chunk,
                "metadata": {
                    "tender_id": tender_id,
                    "chunk_id": i,
                    "source": extraction_result["metadata"].get(
                        "filename",
                        "unknown"
                    ),
                    "page": page_num,
                    "type": "text"
                }
            })

        # Ingest Tables separately to preserve structure
        for i, table in enumerate(extraction_result.get("tables", [])):
            if "markdown" in table:
                documents.append({
                    "page_content": f"Table Caption: {table.get('caption', 'None')}\n\n{table['markdown']}",
                    "metadata": {
                        "tender_id": tender_id,
                        "chunk_id": f"table_{i}",
                        "source": extraction_result["metadata"].get(
                            "filename",
                            "unknown"
                        ),
                        "page": table.get("page") or "N/A",
                        "type": "table"
                    }
                })

        # IMPORTANT:
        # No persistence for now.
        # Avoids sqlite/readonly/streamlit corruption issues.
        self.vectorstore = Chroma.from_texts(
            texts=[doc["page_content"] for doc in documents],
            embedding=self.embeddings,
            metadatas=[doc["metadata"] for doc in documents],
            collection_name=f"tender_{tender_id}"
        )

        st.success(f"✓ Ingested {len(chunks)} text chunks and {len(extraction_result.get('tables', []))} tables")

    def retrieve(self, query: str, k: int = 8):
        """Retrieve diverse relevant chunks"""

        if self.vectorstore is None:
            raise ValueError("No vectorstore loaded.")

        retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": k,
                "fetch_k": 20,
                "lambda_mult": 0.5
            }
        )

        return retriever.invoke(query)
