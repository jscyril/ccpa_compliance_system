---
phase: 4
plan: 1
wave: 1
depends_on: []
files_modified:
  - backend/Dockerfile
autonomous: true

must_haves:
  truths:
    - "Dockerfile uses python:3.13-slim"
    - "Dockerfile does not install local LLMs or use nvidia base images"
    - "Dockerfile pre-downloads the HuggingFace bge-small text embedding model during build"
    - "Dockerfile executes scripts/preprocess_ccpa.py during build"
    - "Dockerfile exposes port 8000 and runs uvicorn directly"
  artifacts:
    - "Dockerfile is completely rewritten"
---

# Plan 4.1: Lightweight Docker Image

## Objective
Rewrite the `Dockerfile` to create a lightweight, production-ready image suitable for deployment on serverless platforms like Google Cloud Run. Since we migrated to the Gemini API, we no longer need GPU support, massive LLM downloads, or complex startup scripts.

Purpose: Delivers REQ-08 from SPEC.md. Reduces image size from ~17GB to ~200MB, significantly improving build times and deployment speed.

## Context
- .gsd/SPEC.md
- backend/Dockerfile (to be replaced)

## Tasks

<task type="auto">
  <name>Rewrite Dockerfile</name>
  <files>backend/Dockerfile</files>
  <action>
    Completely replace the contents of `backend/Dockerfile` with a clean, slim Python image setup:

    1. Base image: `FROM python:3.13-slim`
    2. Set environment variables: `PYTHONDONTWRITEBYTECODE 1` and `PYTHONUNBUFFERED 1`
    3. Install build dependencies (needed for ChromaDB/embeddings): `apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*`
    4. Set `WORKDIR /app`
    5. Copy `requirements.txt` and install: `pip install --no-cache-dir -r requirements.txt`
    6. Copy the application code (`app/` and `scripts/`)
    7. Pre-process the CCPA data: `RUN python scripts/preprocess_ccpa.py`
    8. Pre-download the embedding model so it's cached in the image layer:
       `RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"`
    9. Expose port 8000
    10. Run the app directly with uvicorn: `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`

    AVOID: Do NOT include any `nvidia` base images, `HF_TOKEN` args, or LLM snapshot downloads. Do NOT use the old `startup.sh` script.
  </action>
  <verify>grep -q "python:3.13-slim" backend/Dockerfile && ! grep -q "nvidia/cuda" backend/Dockerfile</verify>
  <done>Dockerfile is completely rewritten to be lightweight and CPU-only.</done>
</task>

<task type="auto">
  <name>Remove legacy startup script</name>
  <files>backend/startup.sh [DELETE]</files>
  <action>
    Delete the `backend/startup.sh` file, as it is no longer needed (the Dockerfile now runs uvicorn directly).
  </action>
  <verify>test ! -f backend/startup.sh</verify>
  <done>startup.sh is deleted.</done>
</task>

<task type="checkpoint:human-verify">
  <name>Verify Docker Build</name>
  <files>none</files>
  <action>
    Build the Docker image locally to ensure all dependencies install correctly, the CCPA data preprocesses, and the embedding model downloads successfully.
  </action>
  <verify>
    cd backend && docker build -t ccpa-analyzer:latest .
  </verify>
  <done>Docker image builds successfully without errors.</done>
</task>

## Success Criteria
- [ ] Dockerfile uses `python:3.13-slim`
- [ ] Dockerfile no longer references `nvidia`, `HF_TOKEN`, or `DeepSeek`
- [ ] Image builds successfully
