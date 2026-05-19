# src/core/extract.py
import streamlit as st
from pathlib import Path
from typing import Dict, Any, Union, BinaryIO
import tempfile
import os

from streamlit.runtime.uploaded_file_manager import UploadedFile
from docling.document_converter import DocumentConverter


PdfInput = Union[str, Path, bytes, UploadedFile, BinaryIO]


def extract_tender_document(pdf_input: PdfInput) -> Dict[str, Any]:
    """
    Extract tender document with page-aware text preservation.
    """

    temp_path = None

    try:
        # ==========================================
        # Handle different input types
        # ==========================================

        if isinstance(pdf_input, UploadedFile):
            pdf_input.seek(0)
            pdf_bytes = pdf_input.read()

        elif isinstance(pdf_input, bytes):
            pdf_bytes = pdf_input

        elif isinstance(pdf_input, (str, Path)):
            pdf_path = Path(pdf_input)
            pdf_bytes = pdf_path.read_bytes()

        else:
            pdf_input.seek(0)
            pdf_bytes = pdf_input.read()

        # ==========================================
        # Save temporary PDF for Docling
        # ==========================================

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp:
            tmp.write(pdf_bytes)
            temp_path = tmp.name

        # ==========================================
        # Run Docling conversion
        # ==========================================

        converter = DocumentConverter()
        result = converter.convert(temp_path)

        doc = result.document

        # ==========================================
        # Full markdown export
        # ==========================================

        full_markdown = doc.export_to_markdown()

        # ==========================================
        # TABLE EXTRACTION
        # ==========================================


        tables = []

        for i, table in enumerate(doc.tables):

            try:
                df = table.export_to_dataframe()

                page_no = None

                if hasattr(table, "prov") and table.prov:

                    for item in table.prov:

                        if hasattr(item, "page_no"):
                            page_no = item.page_no
                            break

                tables.append({
                    "table_index": i,
                    "page": page_no,
                    "caption": str(
                        getattr(table, "caption", "")
                    ),
                    "data": df.to_dict(orient="records"),
                    "markdown": df.to_markdown(index=False)
                })

            except Exception as e:

                tables.append({
                    "table_index": i,
                    "error": f"Table parsing failed: {str(e)[:100]}"
                })

        # ==========================================
        # HIERARCHICAL CHUNKING (New)
        # ==========================================

        from docling_core.transforms.chunker.hierarchical_chunker import HierarchicalChunker
        chunker = HierarchicalChunker()
        doc_chunks = []
        
        for chunk in chunker.chunk(doc):
            # Extract page number from providence if available
            page_no = "N/A"
            if chunk.meta.doc_items:
                # Get page number from the first item's provenance
                first_item = chunk.meta.doc_items[0]
                if hasattr(first_item, "prov") and first_item.prov:
                    page_no = first_item.prov[0].page_no
                elif hasattr(first_item, "page_no"):
                    page_no = first_item.page_no

            doc_chunks.append({
                "text": chunker.contextualize(chunk),
                "page": page_no,
                "metadata": {
                    "page": page_no,
                    "headings": chunk.meta.headings if hasattr(chunk.meta, "headings") else []
                }
            })

        # ==========================================
        # Return structured extraction
        # ==========================================

        return {
            "success": True,
            "full_markdown": full_markdown,
            "doc_chunks": doc_chunks,
            "tables": tables,
            "metadata": {
                "filename": getattr(
                    pdf_input,
                    "name",
                    "unknown.pdf"
                ),
                "page_count": len(doc.pages),
                "table_count": len(tables),
            }
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e),
            "full_markdown": "",
            "tables": [],
            "metadata": {}
        }

    finally:

        if temp_path and os.path.exists(temp_path):

            try:
                os.unlink(temp_path)

            except Exception:
                pass
