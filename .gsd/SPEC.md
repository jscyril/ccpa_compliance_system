# SPEC.md — Project Specification

> **Status**: `FINALIZED`

## Vision
A portfolio-grade CCPA compliance analysis API that uses Google's Gemini API and RAG to analyze business practices against the CCPA statute. Returns rich, structured responses with explanations, cited articles, and violation classifications — streamed in real-time via SSE. Designed as a production-ready backend that a separate frontend team can integrate with immediately.

## Goals
1. **Gemini-powered analysis** — Replace local LLM with Gemini API (configurable flash/pro) for fast, accurate legal reasoning
2. **Rich response schema** — Return harmful status, violated articles, explanation, and referenced statute text
3. **Streaming responses** — SSE endpoint so frontends can display results progressively
4. **Frontend-ready API** — CORS, API key auth, OpenAPI docs, consistent error handling
5. **Lightweight deployment** — ~200MB Docker image deployable to Cloud Run/Railway/Render
6. **High performance** — <2s responses, concurrent request handling, robust error recovery

## Non-Goals (Out of Scope)
- Frontend development (separate team)
- User account management / login flows
- Multi-statute support (GDPR, HIPAA) — future milestone
- Real-time monitoring dashboard

## Users
- **Frontend developers** consuming the REST/SSE API
- **Portfolio reviewers** evaluating system design and code quality
- **End users** (via frontend) analyzing business practices for CCPA compliance

## Constraints
- Gemini API requires a `GEMINI_API_KEY` environment variable
- RAG knowledge base is CCPA-only (45 sections, 212 subsections)
- Must maintain backward compatibility with `POST /analyze` JSON endpoint
- Python 3.11+, FastAPI

## Success Criteria
- [ ] Gemini API integration with flash/pro config toggle
- [ ] Response includes: harmful, articles, explanation, referenced_sections
- [ ] SSE streaming endpoint functional
- [ ] API key authentication working
- [ ] CORS configured for frontend integration
- [ ] Docker image builds and runs under 200MB
- [ ] Response time <2s for typical queries
- [ ] All 10 original test cases pass with new schema
