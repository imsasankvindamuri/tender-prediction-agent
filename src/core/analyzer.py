# src/core/analyzer.py
import streamlit as st
from langchain_core.messages import HumanMessage

from core.llm import get_llm


class TenderAnalyzer:
    def __init__(self, rag):
        self.rag = rag
        self.llm = get_llm()

    def _query_section(self, section_name: str, search_queries: list[str], instructions: str) -> str:
        """Query RAG for a specific section"""
        all_context = []
        citations = []

        for query in search_queries:
            docs = self.rag.retrieve(query, k=5)
            for doc in docs:
                page = doc.metadata.get("page", "N/A")
                all_context.append(doc.page_content)
                citations.append(f"Page {page} (Chunk {doc.metadata.get('chunk_id')})")

        context = "\n\n".join(all_context[:8])  # limit context

        prompt = f"""
You are an expert tender analyst. Use ONLY the provided context.

**Section:** {section_name}

**Instructions:** {instructions}

**Context:**
{context}

Answer concisely and accurately.
If information is not present, say "Not explicitly mentioned".

At the end, add:
**Citations:** {", ".join(set(citations[:6]))}
"""

        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()

    def generate_full_analysis(self) -> str:
        """Generate the complete structured report"""
        report = ["# Tender Analysis Report\n"]

        sections = [
            {
                "title": "1. Critical Information",
                "queries": ["tender reference number", "tender title", "submission deadline", "estimated value", "EMD", "tender fees"],
                "instructions": "Extract tender ID, title, organization, deadlines, value, EMD etc."
            },
            {
                "title": "2. Qualification Criteria",
                "queries": ["eligibility criteria", "qualification requirements", "financial turnover", "certifications", "prior experience"],
                "instructions": "List all eligibility, financial, and experience requirements."
            },
            {
                "title": "3. Technical Proposal Requirements",
                "queries": ["technical requirements", "deliverables", "performance benchmarks", "timeline"],
                "instructions": "Summarize key technical specs and deliverables with timelines."
            },
            {
                "title": "4. SLA and Commercial Terms",
                "queries": ["penalties", "payment terms", "SLA", "commercial clauses", "risky conditions"],
                "instructions": "Extract penalties, payment terms, and risky clauses."
            },
            {
                "title": "5. Risks and Red Flags",
                "queries": ["risks", "red flags", "prohibited", "human oversight", "zero trust", "sovereignty"],
                "instructions": "Highlight missing info, strict requirements, and major risks."
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
