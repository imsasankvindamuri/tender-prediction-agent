# Project Cleanup & Technical Debt

This document tracks "dead code," unused dependencies, and other technical debt identified for future cleanup.

## Unused Dependencies (pyproject.toml)
- **`langchain-text-splitters`**: Previously used for character-based splitting. Replaced by `docling` hierarchical chunking.
- **`protobuf`**: Included as a dependency, but only used via an environment variable in `app.py` to fix a runtime issue. It 
  may not be needed as a direct dependency.

## Dead Code & Constants
- **`src/core/config.py`**:
  - `INITIAL_ANALYSIS_PROMPT`: This large prompt was used in the prototype phase but has been replaced by the modular `sections` 
    logic in `src/core/analyzer.py`.
- **`src/core/extract.py`**:
  - `page_texts`: A list populated with page-by-page markdown. It was an intermediate step that is now redundant because `doc_chunks` 
    provides better hierarchical context.
- **`src/app.py`**:
  - `import os` inside `if __name__ == "__main__":` is fine, but the project structure mentioned in `README.md` (`src/main.py`, 
    `src/utils.py`) is non-existent.

## Unused Imports
- **`src/ui/sidebar.py`**:
  - `traceback`, `tempfile`, `os`: Leftover from earlier extraction logic.
  - `HumanMessage`: Imported from `langchain_core.messages` but never instantiated.
- **`src/core/rag.py`**:
  - `List`: Imported from `typing` but not used in the current type hints.

## Documentation Drift
- **`README.md`**:
  - The "Project Structure" section is outdated. It lists files like `src/main.py` and `src/utils.py` that do not exist in the
    current refactored state.
  - The "Planned Features" section still lists RAG and table-aware parsing as planned, even though they are now implemented.
