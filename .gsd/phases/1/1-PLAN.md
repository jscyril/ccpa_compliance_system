---
phase: 1
plan: 1
wave: 1
depends_on: []
files_modified:
  - backend/requirements.txt
  - backend/app/core/llm_engine.py
  - backend/app/core/config.py
autonomous: true

must_haves:
  truths:
    - "Gemini API generates text when called with a prompt"
    - "Config toggle switches between gemini-2.0-flash and gemini-1.5-pro"
    - "GEMINI_API_KEY env var is read at startup"
  artifacts:
    - "backend/app/core/llm_engine.py uses google-generativeai SDK"
    - "backend/app/core/config.py exists with model toggle"
---

# Plan 1.1: Replace LLM Engine with Gemini API

## Objective
Replace the local HuggingFace LLM (DeepSeek/Qwen, 221 lines, torch + transformers + bitsandbytes) with Google's Gemini API via the `google-generativeai` SDK. Add a config module for model selection.

Purpose: Eliminates GPU dependency, reduces Docker image from 17GB to ~200MB, drops response time from 60-90s to <2s.

## Context
- .gsd/SPEC.md
- .gsd/DECISIONS.md (ADR-001)
- backend/app/core/llm_engine.py (current — 221 lines, to be rewritten)
- backend/app/main.py (imports llm_engine)
- backend/app/services/analyzer.py (calls llm_engine.generate())

## Tasks

<task type="auto">
  <name>Create config module with model toggle</name>
  <files>backend/app/core/config.py</files>
  <action>
    Create a new config module using Pydantic Settings:
    - GEMINI_API_KEY: str (from env, required)
    - GEMINI_MODEL: str (from env, default "gemini-2.0-flash", options: "gemini-2.0-flash", "gemini-1.5-pro")
    - API_KEY: str (from env, for X-API-Key auth — will be used in Phase 3)
    - CORS_ORIGINS: list[str] (from env, default ["*"] — will be used in Phase 3)

    Export a singleton `settings` object.

    AVOID: Don't use python-dotenv — Pydantic Settings reads .env natively.
    AVOID: Don't hardcode any secrets.
  </action>
  <verify>python -c "from app.core.config import settings; print(settings.GEMINI_MODEL)"</verify>
  <done>Config module loads GEMINI_API_KEY and GEMINI_MODEL from environment variables</done>
</task>

<task type="auto">
  <name>Rewrite llm_engine.py to use Gemini API</name>
  <files>backend/app/core/llm_engine.py, backend/requirements.txt</files>
  <action>
    1. Replace requirements.txt: Remove torch, transformers, bitsandbytes, accelerate. Add google-generativeai>=0.8. Keep fastapi, uvicorn, chromadb, sentence-transformers.

    2. Completely rewrite llm_engine.py:
    - Import `google.generativeai as genai`
    - Import `settings` from config
    - Class `LLMEngine` with:
      - `__init__`: stores model reference (None until load())
      - `is_ready` property: returns True when model is configured
      - `load()`: calls `genai.configure(api_key=settings.GEMINI_API_KEY)`, creates `genai.GenerativeModel(settings.GEMINI_MODEL)`, stores it
      - `generate(prompt: str) -> str`: calls `self._model.generate_content(prompt)`, returns `response.text`
      - `generate_stream(prompt: str)`: async generator that yields text chunks via `self._model.generate_content(prompt, stream=True)` — will be used by SSE in Phase 3
    - Keep the same module-level singleton pattern: `llm_engine = LLMEngine()`
    - Keep the same public interface: `load()`, `is_ready`, `generate(prompt)`

    AVOID: Don't use async Gemini client yet — the sync client is simpler and works fine with FastAPI's thread pool.
    AVOID: Don't change the generate() return type — analyzer.py depends on it returning a string.
  </action>
  <verify>
    GEMINI_API_KEY=test python -c "from app.core.llm_engine import LLMEngine; e = LLMEngine(); print(e.is_ready)"
  </verify>
  <done>
    - llm_engine.py uses google-generativeai SDK
    - generate() returns a string (same interface as before)
    - generate_stream() exists for future SSE use
    - requirements.txt no longer includes torch/transformers/bitsandbytes
  </done>
</task>

## Success Criteria
- [ ] `from app.core.config import settings` works and reads env vars
- [ ] `from app.core.llm_engine import llm_engine` imports without torch
- [ ] `llm_engine.generate(prompt)` returns text from Gemini API
- [ ] requirements.txt has no torch, transformers, bitsandbytes, accelerate
- [ ] requirements.txt has google-generativeai
