---
phase: 3
plan: 2
wave: 2
depends_on: ["3.1"]
files_modified:
  - backend/app/services/analyzer.py
  - backend/app/main.py
autonomous: true

must_haves:
  truths:
    - "Streaming endpoint exists and yields Server-Sent Events (SSE)"
    - "Streaming generator is run efficiently without blocking event loop"
  artifacts:
    - "analyzer.py has an analyze_stream method"
    - "main.py has a /analyze/stream endpoint returning StreamingResponse"
---

# Plan 3.2: SSE Streaming Endpoint

## Objective
Add a Server-Sent Events (SSE) endpoint to stream compliance analysis results to the frontend progressively.

Purpose: Delivers REQ-04. Streaming vastly improves perceived performance on the frontend, especially for longer LLM generations like the `explanation` field.

## Context
- .gsd/SPEC.md
- backend/app/services/analyzer.py
- backend/app/main.py
- backend/app/core/llm_engine.py (already has `generate_stream()`)

## Tasks

<task type="auto">
  <name>Add streaming method to Analyzer service</name>
  <files>backend/app/services/analyzer.py</files>
  <action>
    Add an `analyze_stream(self, prompt: str)` method to the `Analyzer` class:
    1. Perform the vector search and parent-document retrieval (same as Step 1 & 2 of `_run_pipeline`).
    2. Build the LLM prompt (Step 3).
    3. Instead of calling `self._llm.generate()`, call and return `self._llm.generate_stream(full_prompt)`.
    
    This method should return the generator object directly.

    AVOID: Don't parse the JSON response here. The streaming endpoint yields raw text chunks (which the frontend will parse or display as a stream).
  </action>
  <verify>python -c "from app.services.analyzer import analyzer; assert hasattr(analyzer, 'analyze_stream'); print('OK')"</verify>
  <done>Analyzer has a method that returns a text chunk generator.</done>
</task>

<task type="auto">
  <name>Create SSE endpoint</name>
  <files>backend/app/main.py</files>
  <action>
    Add the SSE streaming endpoint:
    1. Import `StreamingResponse` from `fastapi.responses`.
    2. Add `GET /analyze/stream` endpoint.
    3. Take `prompt: str` as a query parameter.
    4. Take `api_key: str = Depends(get_api_key)` for security.
    5. Create an inner generator function `event_generator()`:
       - Get the chunk generator: `chunk_gen = analyzer.analyze_stream(prompt)`
       - Loop through chunks: `for chunk in chunk_gen: yield f"data: {json.dumps({'text': chunk})}\n\n"`
       - Wrap in a try/except to handle errors gracefully, yielding an error event if the pipeline fails.
    6. Return `StreamingResponse(event_generator(), media_type="text/event-stream")`.

    Note: FastAPI evaluates sync generators passed to `StreamingResponse` in a managed threadpool, so the synchronous `analyzer.analyze_stream` won't block the main asyncio event loop (fulfills REQ-09 concurrent handling).

    AVOID: Don't forget the `data: ` prefix and `\n\n` suffix required by the SSE protocol.
  </action>
  <verify>python -c "from app.main import app; stream_route = next((r for r in app.routes if r.path == '/analyze/stream'), None); assert stream_route is not None; print('OK')"</verify>
  <done>GET /analyze/stream exists and returns StreamingResponse with media_type="text/event-stream".</done>
</task>

## Success Criteria
- [ ] `analyzer.analyze_stream()` returns a generator
- [ ] `GET /analyze/stream?prompt=...` returns chunked text in SSE format
- [ ] Both `/analyze` and `/analyze/stream` are protected by API key
