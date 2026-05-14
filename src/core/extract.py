# src/core/extract.py
from pathlib import Path
from typing import Dict, Any, Union, BinaryIO
import tempfile
import os

from streamlit.runtime.uploaded_file_manager import UploadedFile
from docling.document_converter import DocumentConverter


PdfInput = Union[str, Path, bytes, UploadedFile, BinaryIO]


def extract_tender_document(pdf_input: PdfInput) -> Dict[str, Any]:
    """
    Robust extraction that handles Streamlit UploadedFile,
    bytes, file-like objects, or filesystem paths.
    """

    temp_path = None

    try:
        # UploadedFile
        if isinstance(pdf_input, UploadedFile):
            pdf_input.seek(0)
            pdf_bytes = pdf_input.read()

        # Raw bytes
        elif isinstance(pdf_input, bytes):
            pdf_bytes = pdf_input

        # File path
        elif isinstance(pdf_input, (str, Path)):
            pdf_path = Path(pdf_input)
            pdf_bytes = pdf_path.read_bytes()

        # Generic file-like object
        else:
            pdf_input.seek(0)
            pdf_bytes = pdf_input.read()

        # Save to temporary file for Docling
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            temp_path = tmp.name

        # Run Docling
        converter = DocumentConverter()
        result = converter.convert(temp_path)
        doc = result.document

        full_markdown = doc.export_to_markdown()

        # Tables
        tables = []

        for i, table in enumerate(doc.tables):
            try:
                df = table.export_to_dataframe()

                tables.append({
                    "table_index": i,
                    "page": getattr(table, "prov", [{}])[0].get("page_no", None),
                    "caption": str(getattr(table, "captions", "")),
                    "data": df.to_dict(orient="records"),
                    "markdown": df.to_markdown(index=False)
                })

            except Exception:
                tables.append({
                    "table_index": i,
                    "error": "Table parsing failed"
                })

        return {
            "success": True,
            "full_markdown": full_markdown,
            "tables": tables,
            "metadata": {
                "filename": getattr(pdf_input, "name", "unknown.pdf"),
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
