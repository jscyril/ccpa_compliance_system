---
phase: 5
plan: 2
wave: 2
depends_on: ["5.1"]
files_modified:
  - README.md
autonomous: true

must_haves:
  truths:
    - "README accurately reflects the Gemini API and lightweight Docker configuration"
    - "Deprecated local LLM instructions are removed"
  artifacts:
    - "README.md"
---

# Plan 5.2: Documentation Polish

## Objective
Update the `README.md` to reflect all architectural changes made during Phases 1-4. The system is now powered by the Gemini API, features a lightweight Docker image without GPU requirements, and supports streaming and API key auth.

Purpose: Finalizes the project for portfolio presentation, ensuring reviewers understand the current architecture and deployment steps.

## Context
- .gsd/SPEC.md
- README.md
- backend/Dockerfile

## Tasks

<task type="auto">
  <name>Update README.md</name>
  <files>README.md</files>
  <action>
    Rewrite the `README.md` to cleanly describe the v2.0 architecture:
    1. Update the Architecture section: Remove DeepSeek/Llama/Qwen. Mention Google Gemini API (via `google-genai`).
    2. Update Key Components: Highlight Gemini, ChromaDB, and FastAPI.
    3. Update Environment Variables: Remove `HF_TOKEN`. Add `GEMINI_API_KEY` (required) and `API_KEY` (optional, for securing the `/analyze` endpoints).
    4. Remove all GPU/VRAM requirement tables. The backend is now API-driven and CPU-light (only handling embeddings via `bge-small`).
    5. Update Docker Run commands to reflect the newly refactored lightweight image (no `--gpus all` needed). Remove HF_TOKEN and add GEMINI_API_KEY.
    6. Update API usage examples to reflect the new 4-field schema (`harmful`, `articles`, `explanation`, `referenced_articles`) and show the `X-API-Key` header requirement if `API_KEY` is set. Also document the new `GET /analyze/stream` endpoint.

    AVOID: Leaving any traces of the old local LLM hackathon setup (e.g., bitandbytes, GPU fallbacks, 17GB image sizes).
  </action>
  <verify>grep -q "GEMINI_API_KEY" README.md && ! grep -q "DeepSeek" README.md</verify>
  <done>README accurately documents the v2.0 Gemini API architecture.</done>
</task>

## Success Criteria
- [ ] README mentions Gemini API, API Key Auth, and SSE stream
- [ ] README has no mentions of `HF_TOKEN` or local GPU requirements
- [ ] API examples show the full new JSON schema
