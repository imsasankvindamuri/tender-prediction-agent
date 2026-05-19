import streamlit as st
from langchain_chroma import Chroma

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from sentence_transformers import CrossEncoder


class TenderRAG:
    """High-fidelity RAG handler with Manual Hybrid Search and Reranking."""

    def __init__(self):
        # High-fidelity local embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Cross-Encoder for Reranking
        self.reranker = CrossEncoder('BAAI/bge-reranker-base')

        self.vectorstore = None
        self.bm25_retriever = None

    def ingest_document(self, extraction_result: dict, tender_id: str):
        """Ingest tender into hybrid search system"""

        if not extraction_result.get("success"):
            raise ValueError("Extraction failed")

        # Use Docling hierarchical chunks
        doc_chunks = extraction_result.get("doc_chunks", [])
        
        documents = []
        texts = []
        metadatas = []

        # 1. Process Text Chunks
        for i, chunk in enumerate(doc_chunks):
            content = chunk["text"]
            metadata = {
                "tender_id": tender_id,
                "chunk_id": f"text_{i}",
                "source": extraction_result["metadata"].get("filename", "unknown"),
                "page": chunk.get("page", "N/A"),
                "type": "text",
                "headings": ", ".join(chunk["metadata"].get("headings", []))
            }
            documents.append({"page_content": content, "metadata": metadata})
            texts.append(content)
            metadatas.append(metadata)

        # 2. Process Tables (Keep them as high-priority chunks)
        for i, table in enumerate(extraction_result.get("tables", [])):
            if "markdown" in table:
                content = f"Table Caption: {table.get('caption', 'None')}\n\n{table['markdown']}"
                metadata = {
                    "tender_id": tender_id,
                    "chunk_id": f"table_{i}",
                    "source": extraction_result["metadata"].get("filename", "unknown"),
                    "page": table.get("page") or "N/A",
                    "type": "table"
                }
                documents.append({"page_content": content, "metadata": metadata})
                texts.append(content)
                metadatas.append(metadata)

        # 3. Setup Vector Store (Chroma)
        self.vectorstore = Chroma.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas,
            collection_name=f"tender_{tender_id}"
        )

        # 4. Setup Keyword Search (BM25)
        # We use from_texts to ensure it uses the same chunking as vector
        self.bm25_retriever = BM25Retriever.from_texts(
            texts,
            metadatas=metadatas
        )
        self.bm25_retriever.k = 20  # Candidates for reranking

        st.success(f"✓ Ingested {len(doc_chunks)} hierarchical chunks and {len(extraction_result.get('tables', []))} tables with Hybrid Search support")

    def retrieve(self, query: str, k: int = 8):
        """Retrieve and Rerank results for maximum precision"""

        if self.vectorstore is None or self.bm25_retriever is None:
            raise ValueError("No vectorstore loaded.")

        # 1. Hybrid Retrieval (Union of BM25 and Vector)
        # Fetching top 20 from each to ensure variety before reranking
        bm25_docs = self.bm25_retriever.invoke(query)
        vector_docs = self.vectorstore.similarity_search(query, k=20)
        
        # Merge and deduplicate based on chunk_id
        seen_ids = set()
        merged_docs = []
        
        for doc in (bm25_docs + vector_docs):
            chunk_id = doc.metadata.get("chunk_id")
            if chunk_id not in seen_ids:
                merged_docs.append(doc)
                seen_ids.add(chunk_id)

        if not merged_docs:
            return []

        # 2. Reranking with Cross-Encoder
        pairs = [[query, doc.page_content] for doc in merged_docs]
        scores = self.reranker.predict(pairs)

        # 3. Sort by reranker score
        for i, doc in enumerate(merged_docs):
            doc.metadata["rerank_score"] = float(scores[i])

        sorted_docs = sorted(
            merged_docs,
            key=lambda x: x.metadata["rerank_score"],
            reverse=True
        )

        # 4. Return top K
        return sorted_docs[:k]
