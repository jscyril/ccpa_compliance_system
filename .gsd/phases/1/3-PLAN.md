---
phase: 1
plan: 3
wave: 2
depends_on: ["1.1", "1.2"]
files_modified:
  - backend/app/main.py
autonomous: true

must_haves:
  truths:
    - "Server starts without loading torch/transformers"
    - "POST /analyze returns correct JSON from Gemini"
    - "GET /health returns 200 when Gemini API is configured"
  artifacts:
    - "main.py startup no longer loads HuggingFace model"
---

# Plan 1.3: Update FastAPI Startup & Integration Test

## Objective
Update main.py startup lifecycle to work with the new Gemini-based LLM engine, and verify the full pipeline end-to-end.

Purpose: This is the integration plan — connects the new LLM engine (Plan 1.1) with the updated prompt builder (Plan 1.2) through the existing analyzer service.

## Context
- .gsd/SPEC.md
- backend/app/main.py (109 lines — lifespan, health, analyze endpoints)
- backend/app/services/analyzer.py (no changes needed — uses llm_engine.generate() interface)
- backend/app/core/llm_engine.py (rewritten in Plan 1.1)

## Tasks

<task type="auto">
  <name>Update main.py startup for Gemini</name>
  <files>backend/app/main.py</files>
  <action>
    Update the lifespan() function:
    1. Remove: logging about "Loading LLM engine" with GPU/VRAM details
    2. Keep: llm_engine.load() call (same interface, now configures Gemini API)
    3. Keep: vector_store.build_index() call (unchanged)
    4. Keep: health endpoint checking llm_engine.is_ready and vector_store.is_ready
    5. Update startup logs to say "Configuring Gemini API" instead of "Loading LLM engine"

    Note: analyzer.py does NOT need changes — it calls llm_engine.generate() which has the same interface.

    AVOID: Don't add CORS or auth yet — that's Phase 3.
    AVOID: Don't change the endpoint signatures.
  </action>
  <verify>GEMINI_API_KEY=test python -c "from app.main import app; print('App created OK')"</verify>
  <done>
    - main.py imports work without torch
    - Startup lifecycle calls llm_engine.load() (Gemini configuration)
    - No references to GPU, VRAM, HuggingFace in startup logs
  </done>
</task>

<task type="checkpoint:human-verify">
  <name>End-to-end integration test</name>
  <files>none (runtime verification)</files>
  <action>
    Start the server and test the full pipeline:
    1. Set GEMINI_API_KEY environment variable
    2. Run: uvicorn app.main:app --port 8000
    3. Wait for SERVER READY
    4. Test health: curl http://localhost:8000/health
    5. Test analyze: curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d '{"prompt": "We sell customer data to third parties without consent."}'
    6. Verify response has harmful=true and valid articles
  </action>
  <verify>
    curl -s http://localhost:8000/health | python -c "import sys,json; d=json.load(sys.stdin); assert d.get('status')=='healthy'"
    curl -s -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d '{"prompt": "We sell customer data without consent."}' | python -c "import sys,json; d=json.load(sys.stdin); assert 'harmful' in d; print(json.dumps(d, indent=2))"
  </verify>
  <done>
    - Health endpoint returns 200
    - Analyze endpoint returns valid JSON with harmful and articles
    - Response time is under 5 seconds
    - No torch/transformers in Python process
  </done>
</task>

## Success Criteria
- [ ] Server starts in <10 seconds (no model download)
- [ ] GET /health returns {"status": "healthy"}
- [ ] POST /analyze returns valid {harmful, articles} JSON
- [ ] Response time <5s for a typical query
- [ ] No torch, transformers, bitsandbytes in the running process
