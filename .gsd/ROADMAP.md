# ROADMAP.md

> **Current Phase**: Not started
> **Milestone**: v1.0

## Must-Haves (from SPEC)
- [ ] Local sub-8B LLM inference via HuggingFace Transformers
- [ ] CCPA statute JSON knowledge base extracted from PDF
- [ ] RAG-style prompt construction grounding LLM in statute text
- [ ] Strict JSON schema output (`harmful` + `articles`)
- [ ] FastAPI server with `/analyze` and `/health` endpoints
- [ ] Docker containerization
- [ ] Pass all 10 automated test cases

## Phases

### Phase 1: Data Foundation
**Status**: ⬜ Not Started
**Objective**: Extract CCPA statute from PDF into structured `ccpa_sections.json` and build the knowledge retrieval layer.
**Requirements**: REQ-01

### Phase 2: LLM Engine & Prompt Engineering
**Status**: ⬜ Not Started
**Objective**: Implement model loading, prompt template with CCPA context injection, and response parsing for strict JSON output.
**Requirements**: REQ-02, REQ-03, REQ-04, REQ-09, REQ-10

### Phase 3: API & Service Integration
**Status**: ⬜ Not Started
**Objective**: Wire up FastAPI endpoints, Pydantic schemas, and the analyzer service that orchestrates the full pipeline.
**Requirements**: REQ-05, REQ-06

### Phase 4: Docker & Deployment
**Status**: ⬜ Not Started
**Objective**: Write Dockerfile, startup script, and verify the containerized system passes all test cases.
**Requirements**: REQ-07, REQ-08
