# DECISIONS.md — Architectural Decision Records

## ADR-001: Switch from Local LLM to Gemini API
**Date**: 2026-03-02
**Status**: Accepted
**Context**: The hackathon version used DeepSeek-R1-Distill-Llama-8B (16GB, slow on CPU, requires NVIDIA GPU for good perf). For a portfolio project, we need fast demos and easy deployment.
**Decision**: Use Google Gemini API with a config toggle between gemini-2.0-flash (fast/cheap) and gemini-1.5-pro (more accurate).
**Consequence**: Docker image drops from ~17GB to ~200MB. No GPU required. Response time drops from 60-90s to <2s. Requires GEMINI_API_KEY env var.

## ADR-002: SSE Streaming over WebSocket
**Date**: 2026-03-02
**Status**: Accepted
**Context**: Frontend team needs progressive response display. Options: WebSocket or SSE.
**Decision**: Use Server-Sent Events (SSE). Simpler than WebSocket for our request-response pattern. Frontend uses native EventSource API.
**Consequence**: Easier to implement, test, and debug. No persistent connection management.

## ADR-003: API Key Authentication
**Date**: 2026-03-02
**Status**: Accepted
**Context**: Need auth that recognizes the app without requiring user login.
**Decision**: API key via X-API-Key header. Key is set as env var on the backend. Frontend embeds the key.
**Consequence**: Simple, stateless, no token refresh. Sufficient for portfolio demo.

## ADR-004: Keep RAG Pipeline
**Date**: 2026-03-02
**Status**: Accepted
**Context**: Even with Gemini's large context, RAG improves accuracy by surfacing the most relevant statute sections.
**Decision**: Keep ChromaDB + bge-small-en-v1.5 embeddings. Feed top-5 sections to Gemini.
**Consequence**: Better citation accuracy. Demonstrates RAG architecture knowledge in portfolio.
