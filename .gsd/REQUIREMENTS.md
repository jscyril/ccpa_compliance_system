# REQUIREMENTS.md

| ID | Requirement | Source | Status |
|----|-------------|--------|--------|
| REQ-01 | Replace local LLM with Gemini API (google-generativeai SDK) | Goal 1 | Pending |
| REQ-02 | Config toggle between gemini-2.0-flash and gemini-1.5-pro | Goal 1 | Pending |
| REQ-03 | Expand AnalyzeResponse: harmful, articles, explanation, referenced_sections | Goal 2 | Pending |
| REQ-04 | SSE streaming endpoint (GET /analyze/stream) | Goal 3 | Pending |
| REQ-05 | CORS middleware with configurable origins | Goal 4 | Pending |
| REQ-06 | API key authentication via X-API-Key header | Goal 4 | Pending |
| REQ-07 | Lightweight Dockerfile (~200MB, no GPU deps) | Goal 5 | Pending |
| REQ-08 | Response time <2s for typical queries | Goal 6 | Pending |
| REQ-09 | Concurrent request handling (async throughout) | Goal 6 | Pending |
| REQ-10 | Backward-compatible POST /analyze endpoint | Constraint | Pending |
