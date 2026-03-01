# DECISIONS.md — Architecture Decision Records

> Format: `ADR-{N}: {Title} — {Date}`

## ADR-1: Llama 3.1 8B Instruct as primary LLM — 2026-03-01

**Context**: Need a sub-8B parameter model with strong instruction-following for JSON output.
**Decision**: Llama 3.1 8B Instruct as primary, Mistral-7B-v0.3 as fallback.
**Rationale**: Best-in-class instruction following for structured output. 4-bit quantization via bitsandbytes to fit in consumer GPU VRAM.

## ADR-2: ChromaDB for in-memory vector search — 2026-03-01

**Context**: Need a vector DB for RAG retrieval inside a Docker container.
**Decision**: ChromaDB running in-memory (no persistence needed).
**Rationale**: Lightweight, zero-config, no external service. Qdrant was considered but heavier for a single-container deployment.

## ADR-3: Parent-Document Retrieval over flat chunking — 2026-03-01

**Context**: Legal text has interconnected clauses. Small chunks lose context.
**Decision**: Embed subsection-level chunks (child), but retrieve full section text (parent) for the LLM prompt.
**Rationale**: Child chunks provide precise semantic matching. Parent sections give the LLM full legal context for accurate article identification.

## ADR-4: Confidence fallback to avoid zero-marks trap — 2026-03-01

**Context**: Citing an incorrect article results in zero marks. 
**Decision**: When LLM output is unparseable or confidence is low, return `{"harmful": false, "articles": []}`.
**Rationale**: Conservative strategy — it's better to miss a violation than to cite a wrong article.

## ADR-5: bge-small-en-v1.5 for embeddings — 2026-03-01

**Context**: Need an embedding model that fits alongside the 8B LLM in VRAM.
**Decision**: BAAI/bge-small-en-v1.5 via sentence-transformers.
**Rationale**: Only 130MB, top-tier performance for its size on MTEB. Leaves VRAM headroom for the quantized LLM.
