---
phase: 3
plan: 1
wave: 1
---

# Plan 3.1: FastAPI Server & Service Orchestration

## Objective
Wire all Phase 1 and 2 components into a working FastAPI application with Pydantic validation, analyzer orchestration, and health check endpoint.

## Context
- .gsd/SPEC.md
- .gsd/ARCHITECTURE.md
- backend/app/schemas/api.py (empty stub)
- backend/app/services/analyzer.py (empty stub)
- backend/app/core/llm_engine.py (Phase 2)
- backend/app/core/vector_store.py (Phase 2)
- backend/app/services/ccpa_knowledge.py (Phase 1)
- backend/app/services/prompt_builder.py (Phase 2)
- backend/app/core/response_parser.py (Phase 2)

## Tasks

<task type="auto">
  <name>Implement Pydantic schemas</name>
  <files>backend/app/schemas/api.py</files>
  <action>
    Create Pydantic models for the API contract:

    1. `AnalyzeRequest`:
       - `prompt: str` — the business practice description

    2. `AnalyzeResponse`:
       - `harmful: bool` — whether the practice violates CCPA
       - `articles: list[str]` — list of violated sections (empty if not harmful)

    Keep these minimal — they exist to validate request/response shape only.

    AVOID: Do NOT add optional fields or default values to AnalyzeRequest.
    AVOID: Do NOT add extra fields (no descriptions, no confidence scores).
  </action>
  <verify>cd backend && python -c "
from app.schemas.api import AnalyzeRequest, AnalyzeResponse
req = AnalyzeRequest(prompt='test')
assert req.prompt == 'test'
resp = AnalyzeResponse(harmful=True, articles=['Section 1798.120'])
assert resp.harmful is True
assert resp.articles == ['Section 1798.120']
print('Schemas validated')
"</verify>
  <done>AnalyzeRequest and AnalyzeResponse Pydantic models validate correctly</done>
</task>

<task type="auto">
  <name>Implement analyzer service orchestration</name>
  <files>backend/app/services/analyzer.py</files>
  <action>
    Create an `Analyzer` class that orchestrates the full compliance analysis pipeline:

    1. `__init__()`: Store references to the singletons:
       - `ccpa_kb` from services
       - `vector_store` from core
       - `llm_engine` from core
       - `prompt_builder` from services

    2. `analyze(prompt: str) -> dict`:
       a. Use `vector_store.search(prompt, top_k=5)` to find relevant subsections
       b. Use `ccpa_kb.get_parent_sections(subsection_ids)` to get full parent sections
       c. Use `prompt_builder.build_prompt(prompt, parent_sections)` to construct the LLM prompt
       d. Use `llm_engine.generate(full_prompt)` to run inference
       e. Use `parse_response(raw_output)` to extract validated JSON
       f. Return the parsed dict

    3. Wrap the entire pipeline in a try/except — on ANY error, return the safe default:
       `{"harmful": false, "articles": []}`

    Create a module-level singleton: `analyzer = Analyzer()`

    CRITICAL: Import `parse_response` from `app.core.response_parser`.
    CRITICAL: The method must return a plain dict, not a Pydantic model.
  </action>
  <verify>cd backend && python -c "
from app.services.analyzer import Analyzer
a = Analyzer()
print('Has analyze:', hasattr(a, 'analyze'))
print('Analyzer instantiates without error')
"</verify>
  <done>Analyzer class instantiates and has analyze() method that orchestrates the full pipeline</done>
</task>

<task type="auto">
  <name>Implement FastAPI main application</name>
  <files>backend/app/main.py (NEW)</files>
  <action>
    Create the FastAPI application entry point:

    1. `app = FastAPI(title="CCPA Compliance Analyzer")`

    2. Startup event (`@app.on_event("startup")` or lifespan):
       - Load the LLM engine: `llm_engine.load()`
       - Build the vector index: `vector_store.build_index(ccpa_kb.get_all_subsections())`
       - Log: "Server ready"

    3. `GET /health`:
       - Return HTTP 200 with `{"status": "healthy"}` when LLM and vector store are ready
       - Return HTTP 503 if not ready

    4. `POST /analyze`:
       - Accept `AnalyzeRequest` body
       - Call `analyzer.analyze(request.prompt)`
       - Return `AnalyzeResponse` with the result
       - On ANY exception → return `{"harmful": false, "articles": []}`

    5. Global error handler:
       - Catch all unhandled exceptions → return safe default JSON

    CRITICAL: The /analyze endpoint must return ONLY the JSON schema, no wrapping.
    CRITICAL: Use `response_model=AnalyzeResponse` to enforce Pydantic validation.
    CRITICAL: Port 8000 is configured in startup.sh, not in main.py.
    AVOID: Do NOT add CORS, authentication, or any middleware not needed.
  </action>
  <verify>cd backend && python -c "
from app.main import app
from fastapi.testclient import TestClient
# Only verify the app object exists and has routes
routes = [r.path for r in app.routes]
print(f'Routes: {routes}')
assert '/analyze' in routes, 'Missing /analyze route'
assert '/health' in routes, 'Missing /health route'
print('FastAPI app has correct routes')
"</verify>
  <done>FastAPI app has /analyze and /health routes, startup loads model and builds index</done>
</task>

## Success Criteria
- [ ] Pydantic schemas validate request/response shape
- [ ] Analyzer orchestrates: vector search → prompt → LLM → parse
- [ ] FastAPI app has /analyze (POST) and /health (GET) endpoints
- [ ] Startup event loads LLM and builds vector index
- [ ] All errors caught → safe default JSON response
