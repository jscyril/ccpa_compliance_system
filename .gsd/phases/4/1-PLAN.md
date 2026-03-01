---
phase: 4
plan: 1
wave: 1
---

# Plan 4.1: Dockerfile, Startup Script & Module Wiring

## Objective
Containerize the application into a Docker image that starts a FastAPI server on port 8000, pre-downloads the model and embeddings during build, and wires up all module __init__.py exports cleanly.

## Context
- .gsd/SPEC.md
- .gsd/ARCHITECTURE.md
- backend/Dockerfile (empty stub)
- backend/startup.sh (empty stub)
- backend/requirements.txt
- backend/app/main.py (Phase 3)
- backend/app/core/llm_engine.py (Phase 2)
- backend/app/core/vector_store.py (Phase 2)
- backend/scripts/preprocess_ccpa.py (Phase 1)

## Tasks

<task type="auto">
  <name>Write startup.sh</name>
  <files>backend/startup.sh</files>
  <action>
    Create a bash startup script that:
    1. Starts with `#!/bin/bash` and `set -e`
    2. Runs uvicorn pointing to `app.main:app`
    3. Binds to `0.0.0.0:8000`
    4. Uses `--timeout-keep-alive 300` (for long inference requests)
    5. Uses `--workers 1` (single GPU, single worker)

    Keep it minimal — just the uvicorn command.

    AVOID: Do NOT add model download or preprocessing here — that's done in Docker build.
    AVOID: Do NOT add environment variable exports — those come from Docker.
  </action>
  <verify>head -5 backend/startup.sh && bash -n backend/startup.sh && echo "Syntax OK"</verify>
  <done>startup.sh runs uvicorn on 0.0.0.0:8000 with timeout and single worker</done>
</task>

<task type="auto">
  <name>Wire up __init__.py module exports</name>
  <files>
    backend/app/__init__.py
    backend/app/core/__init__.py
    backend/app/schemas/__init__.py
  </files>
  <action>
    Ensure all Python package directories have proper __init__.py files:

    1. `backend/app/__init__.py` — empty (just makes it a package)
    2. `backend/app/core/__init__.py` — export key singletons:
       ```python
       from .llm_engine import llm_engine
       from .vector_store import vector_store
       from .response_parser import parse_response
       ```
    3. `backend/app/schemas/__init__.py` — export schemas:
       ```python
       from .api import AnalyzeRequest, AnalyzeResponse
       ```

    Note: `backend/app/services/__init__.py` was already created in Phase 1.

    ONLY create or update files that are empty stubs or missing.
    Do NOT modify files that already have content.
  </action>
  <verify>cd backend && python -c "
import app
import app.core
import app.schemas
import app.services
print('All packages import successfully')
"</verify>
  <done>All Python packages have __init__.py with correct exports</done>
</task>

<task type="auto">
  <name>Write multi-stage Dockerfile</name>
  <files>backend/Dockerfile</files>
  <action>
    Create a Dockerfile that:

    1. Uses `python:3.11-slim` as base (NOT 3.14 — chromadb/pydantic v1 incompatible)
    2. Sets working directory to `/app`
    3. Installs system dependencies: `build-essential` (for bitsandbytes compilation)
    4. Copies and installs `requirements.txt` first (layer caching)
    5. Copies the entire `app/` directory
    6. Copies `scripts/` directory
    7. Pre-runs the CCPA extraction script:
       `RUN python scripts/preprocess_ccpa.py`
       This generates `app/data/ccpa_sections.json` during build.
    8. Pre-downloads the embedding model during build:
       ```
       RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"
       ```
       This caches bge-small (~130MB) in the image layer.
    9. Copies `startup.sh` and makes it executable
    10. Sets `HF_TOKEN` as a build argument AND runtime env var:
        ```
        ARG HF_TOKEN
        ENV HF_TOKEN=${HF_TOKEN}
        ```
    11. Pre-downloads the LLM model during build (saves startup time):
        ```
        RUN python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('meta-llama/Llama-3.1-8B-Instruct', token='${HF_TOKEN}')"
        ```
        Note: Full model download at build time requires HF_TOKEN as build arg.
        If this makes the image too large, it can be downloaded at startup instead.
    12. Exposes port 8000
    13. CMD: `["bash", "startup.sh"]`

    CRITICAL: Use `python:3.11-slim` — NOT 3.14 (chromadb incompatible).
    CRITICAL: HF_TOKEN must be passed as `--build-arg HF_TOKEN=$HF_TOKEN`.
    CRITICAL: Pre-download embedding model during build to avoid download at startup.
    AVOID: Do NOT use multi-stage build — single stage is simpler for ML images.
    AVOID: Do NOT install CUDA in Docker — use nvidia runtime via docker run.
  </action>
  <verify>head -20 backend/Dockerfile && echo "---" && tail -5 backend/Dockerfile</verify>
  <done>Dockerfile uses python:3.11-slim, pre-downloads models, exposes port 8000, runs startup.sh</done>
</task>

## Success Criteria
- [ ] startup.sh runs uvicorn on 0.0.0.0:8000
- [ ] All __init__.py files export correctly
- [ ] Dockerfile uses python:3.11-slim
- [ ] Embedding model pre-downloaded during build
- [ ] CCPA sections JSON generated during build
- [ ] HF_TOKEN passed as build arg and env var
- [ ] Port 8000 exposed, CMD runs startup.sh
