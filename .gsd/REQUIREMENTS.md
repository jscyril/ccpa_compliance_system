# REQUIREMENTS.md

## Format
| ID | Requirement | Source | Status |
|----|-------------|--------|--------|
| REQ-01 | Extract CCPA statute from PDF into structured JSON knowledge base | SPEC goal 1 | Pending |
| REQ-02 | Load and initialize a sub-8B parameter LLM from HuggingFace using `HF_TOKEN` env var | SPEC goal 4, constraints | Pending |
| REQ-03 | Build a prompt template that grounds LLM reasoning in CCPA statute sections (RAG) | SPEC goal 1 | Pending |
| REQ-04 | Parse LLM output into strict `{"harmful": bool, "articles": [...]}` JSON schema | SPEC goal 2 | Pending |
| REQ-05 | Expose `POST /analyze` endpoint accepting `{"prompt": "..."}` and returning valid JSON | SPEC goal 2 | Pending |
| REQ-06 | Expose `GET /health` endpoint returning HTTP 200 when server is ready | SPEC goal 3 | Pending |
| REQ-07 | Containerize the entire system with Docker (single image, port 8000) | SPEC goal 4, constraints | Pending |
| REQ-08 | Pass all 10 automated test cases (5 harmful, 5 safe) within latency constraints | SPEC success criteria | Pending |
| REQ-09 | Never hardcode `HF_TOKEN` — accept only as environment variable | SPEC non-goals, constraints | Pending |
| REQ-10 | Response must contain zero extra text, markdown, or explanation — strict JSON only | SPEC goal 2 | Pending |
