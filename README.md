# Tender Prediction Agent

A lightweight AI-powered tender analysis system built with Python, Streamlit, and LLMs.

This project is currently a Proof of Concept (PoC) focused on:

* Parsing tender PDFs
* Extracting tender text
* Performing AI-assisted tender analysis
* Identifying critical procurement information
* Enabling conversational querying over tender documents

The current architecture intentionally uses direct long-context prompting to evaluate raw model
capabilities before introducing Retrieval-Augmented Generation (RAG).

---

# Features

## Current Features

* PDF tender upload
* Tender text extraction
* AI-generated structured tender analysis
* Conversational follow-up questions
* Streamlit UI
* Groq-powered inference backend
* Long-context tender experimentation

## Planned Features

* Chunked summarization pipeline
* Retrieval-Augmented Generation (RAG)
* Vector search
* Citation grounding
* Page-aware references
* Structured clause extraction
* Tender risk scoring
* Table-aware parsing
* Procurement ontology mapping
* Multi-model backend support

---

# Project Structure

```text
.
├── docs
├── poetry.lock
├── pyproject.toml
├── README.md
├── src
│   ├── app.py
│   ├── main.py
│   └── utils.py
├── tests
└── uploads
```

## Directory Overview

| Directory  | Purpose                                  |
| ---------- | ---------------------------------------- |
| `docs/`    | Research notes and architecture planning |
| `src/`     | Main application source code             |
| `tests/`   | Test suite                               |
| `uploads/` | Uploaded tender PDFs (gitignored)        |

---

# Tech Stack

## Backend

* Python 3.11+
* Streamlit
* LangChain
* Groq API

## LLM

Default model:

```text
llama-3.1-8b-instant
```

The backend is designed to remain OpenAI-compatible for future provider flexibility.

---

# Installation

## Clone the repository

```bash
git clone <repo-url>
cd tender-prediction-agent
```

## Install dependencies

Using Poetry:

```bash
poetry install
```

Activate the environment:

```bash
poetry shell
```

---

# Environment Variables

Create a `.env` file in the project root.

Example:

```env
GROQ_API_KEY=your_api_key_here
```

---

# Running the Application

Run the Streamlit application:

```bash
streamlit run src/app.py
```

The UI should open automatically in your browser.

---

# Current Architecture

The current PoC uses a direct long-context prompting strategy.

Pipeline:

```text
PDF -> Text Extraction -> Full Context Prompt -> LLM Analysis
```

This architecture is intentionally simple in order to:

* Benchmark raw long-context performance
* Measure hallucination tendencies
* Identify context window limitations
* Test semantic extraction quality
* Stress-test procurement reasoning

---

# Known Limitations

The current implementation does NOT yet include:

* Chunking
* Retrieval-Augmented Generation (RAG)
* Embeddings
* Citation grounding
* Structured extraction pipelines
* Page-aware references
* Table-aware parsing
* Semantic reranking

Large tender documents may exceed provider TPM/context limits.

---

# Planned Near-Term Improvements

## Phase 1 — Token-Aware Chunking

Goal:

```text
Large Tender -> Chunks -> Chunk Summaries -> Final Summary
```

This reduces:

* Token pressure
* TPM failures
* Context dilution

Planned library:

```bash
poetry add tiktoken
```

---

## Phase 2 — Retrieval-Augmented Generation (RAG)

Future architecture:

```text
PDF
  ↓
Chunking
  ↓
Embeddings
  ↓
Vector Store
  ↓
Retriever
  ↓
LLM
```

Potential tooling:

* FAISS
* ChromaDB
* LangChain retrievers
* OpenAI embeddings
* Instructor embeddings

---

# Example Analysis Categories

The assistant currently extracts:

* Tender reference numbers
* Important deadlines
* EMD and fees
* Qualification criteria
* Technical requirements
* Commercial terms
* SLA conditions
* Risks and red flags

---

# Design Philosophy

This project intentionally prioritizes:

* Simplicity
* Fast iteration
* Architectural clarity
* Observable failure modes

before introducing:

* complex retrieval pipelines
* agentic orchestration
* production optimization

The goal is to understand the behavior and limitations of LLM-based tender analysis systems incrementally.

---

# Future Research Directions

Potential advanced capabilities:

* Clause graph extraction
* Cross-document procurement analysis
* Adversarial tender detection
* Risk scoring systems
* Procurement recommendation engines
* Tender similarity clustering
* Compliance automation
* Multi-agent procurement workflows

---

# Disclaimer

This project is experimental and intended for research, prototyping, and educational purposes.

AI-generated analysis should not be treated as legal, financial, or procurement advice.

