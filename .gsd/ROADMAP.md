# ROADMAP.md

> **Current Phase**: Not started
> **Milestone**: v1.0

## Must-Haves (from SPEC)
- [ ] Local sub-8B LLM inference (Llama 3.1 8B Instruct, 4-bit quantized)
- [ ] CCPA statute JSON knowledge base extracted from PDF (PyMuPDF)
- [ ] Hybrid RAG: ChromaDB vector search + parent-document retrieval
- [ ] Embeddings via bge-small-en-v1.5 (sentence-transformers)
- [ ] Few-shot prompt engineering with confidence fallback
- [ ] Strict JSON schema output (`harmful` + `articles`)
- [ ] FastAPI server with `/analyze` and `/health` endpoints
- [ ] Docker containerization with pre-computed embeddings

## Phases

### Phase 1: Data Foundation
**Status**: ✅ Complete
**Objective**: Extract CCPA statute from PDF into structured `ccpa_sections.json` with hierarchical parent-child chunks.
**Requirements**: REQ-01
**Key Tasks**:
- Parse `ccpa_statute.pdf` using PyMuPDF, preserving Section → Subsection → Paragraph hierarchy
- Output `ccpa_sections.json` with parent (full section) and child (subsection) structure
- Implement `ccpa_knowledge.py` to load sections and support parent-document retrieval
- Add `PyMuPDF`, `chromadb`, `sentence-transformers` to `requirements.txt`

### Phase 2: LLM Engine & RAG Pipeline
**Status**: ✅ Complete
**Objective**: Wire up quantized LLM, vector search, prompt engineering, and strict JSON parsing.
**Requirements**: REQ-02, REQ-03, REQ-04, REQ-09, REQ-10
**Key Tasks**:
- Load Llama 3.1 8B Instruct with `bitsandbytes` 4-bit quantization (HF_TOKEN from env)
- Build ChromaDB in-memory vector store with bge-small-en-v1.5 embeddings
- Design few-shot prompt template (system prompt + 3 examples + retrieved context)
- Implement response parser with JSON extraction, validation, and confidence fallback
- Add `bitsandbytes`, `accelerate` to `requirements.txt`

### Phase 3: API & Service Integration
**Status**: ⬜ Not Started
**Objective**: FastAPI endpoints, Pydantic schemas, and analyzer orchestration.
**Requirements**: REQ-05, REQ-06
**Key Tasks**:
- Create `main.py` with FastAPI app (startup event loads model + builds index)
- Define `AnalyzeRequest` / `AnalyzeResponse` Pydantic models in `schemas/api.py`
- Implement `analyzer.py`: vector search → prompt build → LLM inference → parse response
- Error handler: exceptions → `{"harmful": false, "articles": []}`

### Phase 4: Docker & Deployment
**Status**: ⬜ Not Started
**Objective**: Containerize and validate against all 10 test cases.
**Requirements**: REQ-07, REQ-08
**Key Tasks**:
- Multi-stage Dockerfile (python:3.11-slim, pre-download model weights during build)
- Write `startup.sh` (uvicorn on 0.0.0.0:8000)
- Verify: all 10 test cases pass, <120s per request, <300s startup
