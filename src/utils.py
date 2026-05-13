# Small util functions

from pymupdf import open as pdfopen
from pathlib import Path

def extract_pdf_text(path: Path | str) -> list[str]:
    pdfpath = Path(path)
    
    if not pdfpath.exists():
        raise FileNotFoundError(f"File not found: '{path}'")
    if not pdfpath.is_file():
        raise IsADirectoryError(f"Expected a file, got a directory: '{path}'")
    if pdfpath.suffix.lower() != ".pdf":
        raise ValueError(f"Expected PDF file, got '{pdfpath.suffix or 'no extension'}'")
    if pdfpath.stat().st_size == 0:
        raise ValueError(f"PDF file is empty: '{path}'")

    pdf_doc = pdfopen(pdfpath)
    try:
        return [str(page.get_text(sort=True)) for page in pdf_doc]
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF '{path}': {e}") from e
    finally:
        pdf_doc.close()

if __name__ == "__main__":
    ...
