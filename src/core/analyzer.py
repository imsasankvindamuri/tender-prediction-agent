# src/core/analyzer.py
import streamlit as st
from langchain_core.messages import HumanMessage

from core.llm import get_llm


class TenderAnalyzer:
    def __init__(self, rag):
        self.rag = rag
        self.llm = get_llm()

    def _query_section(
        self,
        section_name: str,
        search_queries: list[str],
        instructions: str
    ) -> str:
        """Query RAG for a specific section"""

        all_context = []
        citations = []
        seen_chunks = set()

        for query in search_queries:
            # Using k=10 from Hybrid+Rerank to ensure high variety but high precision
            docs = self.rag.retrieve(query, k=10)

            st.write(f"### Retrieval Query: {query}")

            for doc in docs:
                chunk_id = doc.metadata.get("chunk_id")

                # Deduplicate repeated chunks
                if chunk_id in seen_chunks:
                    continue

                seen_chunks.add(chunk_id)

                page = doc.metadata.get("page", "N/A")
                chunk_type = doc.metadata.get("type", "text")

                citations.append(
                    f"Page {page} ({chunk_type.capitalize()} Chunk {chunk_id})"
                )

                all_context.append(doc.page_content)

                # Retrieval logging (truncated for UI)
                st.code(
                    f"""
    TYPE: {chunk_type.upper()} | PAGE: {page} | SCORE: {doc.metadata.get('rerank_score', 0):.4f}
    
    {doc.page_content[:300]}...
                    """
                )

        # Slice to top 12 chunks after reranking for optimal balance of context and noise
        context = "\n\n---\n\n".join(all_context[:12])

        prompt = f"""
    You are an expert tender analyst with a focus on 100% accuracy and zero hallucinations.

    INSTRUCTIONS:
    {instructions}

    SECTION BEING ANALYZED:
    {section_name}

    CONTEXT FROM TENDER:
    {context}

    STRICT RULES:
    1. Use ONLY the provided context. If information is missing, say: "Not explicitly mentioned in the provided document."
    2. NO HALLUCINATIONS. Do not assume or infer details not present.
    3. MANDATORY GROUNDING: For every factual claim, provide a brief supporting quote from the context.
    4. CITATIONS: Use (Page X) after every claim/quote.
    5. Format as clean, professional Markdown with bullet points or tables where appropriate.

    EXAMPLE FORMAT:
    - **Requirement**: The bidder must have X years of experience.
      > "Bidder shall demonstrate at least 5 years of domain expertise" (Page 12)

    Return the analysis for {section_name}:
    """

        response = self.llm.invoke([
            HumanMessage(content=prompt)
        ])

        return str(response.content).strip()

    def generate_full_analysis(self) -> str:
        """Generate the complete structured report"""
        report = ["# Tender Analysis Report\n"]

        sections = [
            {
                "title": "1. Critical Information",
                "queries": ["tender reference number", "tender title", "submission deadline", "estimated value", "EMD fee", "tender fees"],
                "instructions": "Extract primary identifiers: Tender ID/Ref, Title, Authority, Deadlines, and exact Fees/EMD values."
            },
            {
                "title": "2. Qualification Criteria",
                "queries": ["eligibility criteria", "financial turnover requirements", "net worth", "technical experience", "certifications required"],
                "instructions": "Detail all mandatory eligibility, financial, and technical experience requirements. Be precise about numbers."
            },
            {
                "title": "3. Technical Specifications & Deliverables",
                "queries": ["technical requirements", "scope of work", "deliverables", "milestones", "performance standards"],
                "instructions": "Summarize the technical scope and list all key deliverables with their associated timelines or milestones."
            },
            {
                "title": "4. SLA, Penalties & Commercial Terms",
                "queries": ["penalties", "liquidated damages", "payment terms", "service level agreements", "termination clauses"],
                "instructions": "List all penalty clauses, payment schedules, and critical commercial terms."
            },
            {
                "title": "5. Risks, Red Flags & Ambiguities",
                "queries": ["risks", "red flags", "prohibited", "restrictive clauses", "missing information"],
                "instructions": "Identify potential risks, unusually strict clauses, and critical information that appears to be missing."
            }
        ]

        for section in sections:
            st.info(f"Analyzing {section['title']}...")
            content = self._query_section(
                section_name=section["title"],
                search_queries=section["queries"],
                instructions=section["instructions"]
            )
            report.append(f"## {section['title']}")
            report.append(content)
            report.append("\n---\n")

        return "\n".join(report)
