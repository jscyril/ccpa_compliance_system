# ROADMAP.md

> **Current Phase**: Not started
> **Milestone**: v2.0 — Portfolio Edition

## Must-Haves (from SPEC)
- [ ] Gemini API with flash/pro toggle
- [ ] Rich response schema (harmful, articles, explanation, referenced_sections)
- [ ] SSE streaming endpoint
- [ ] API key auth + CORS
- [ ] Lightweight Docker image
- [ ] <2s response time

## Phases

### Phase 1: Gemini API Migration
**Status**: ⬜ Not Started
**Objective**: Replace local LLM engine with Gemini API, add config toggle
**Requirements**: REQ-01, REQ-02

### Phase 2: Rich Response Schema & Prompt Engineering
**Status**: ⬜ Not Started
**Objective**: Expand response to include explanation and referenced statute text. Redesign prompts for Gemini's strengths.
**Requirements**: REQ-03

### Phase 3: API Hardening & Frontend Integration
**Status**: ⬜ Not Started
**Objective**: Add CORS, API key auth, SSE streaming, OpenAPI docs, async throughout
**Requirements**: REQ-04, REQ-05, REQ-06, REQ-09, REQ-10

### Phase 4: Docker & Deployment
**Status**: ⬜ Not Started
**Objective**: Lightweight Dockerfile, Cloud Run ready, environment config, README update
**Requirements**: REQ-07, REQ-08

### Phase 5: Polish & Verification
**Status**: ⬜ Not Started
**Objective**: End-to-end testing, performance benchmarks, documentation

---

## Future Phases (Post v2.0)
- **Batch analysis** — Analyze multiple practices in one request
- **Confidence scores** — Return confidence level per violation
- **Historical analysis** — Cache and compare past analyses
- **Rate limiting** — Per-key rate limits with Redis
- **Multi-statute** — GDPR, HIPAA support
