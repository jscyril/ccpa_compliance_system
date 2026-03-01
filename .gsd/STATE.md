# STATE.md — Project Memory

> Last updated: 2026-03-01T16:50:00+05:30

## Current Position
- **Phase**: 1
- **Task**: Planning complete
- **Status**: Ready for execution

## Next Steps
1. `/execute 1` — Run Plan 1.1 and Plan 1.2

## Architecture Decisions (Summary)
- **LLM**: Llama 3.1 8B Instruct, 4-bit quantized via bitsandbytes
- **Embeddings**: BAAI/bge-small-en-v1.5 (sentence-transformers)
- **Vector DB**: ChromaDB in-memory
- **Retrieval**: Parent-document retrieval (embed subsections, retrieve full sections)
- **Prompting**: Few-shot (3 examples) + system prompt
- **Fallback**: Unparseable/low-confidence output → `{"harmful": false, "articles": []}`
- **PDF parsing**: PyMuPDF (fitz)

## Session Context
- CCPA statute PDF added at `backend/app/data/ccpa_statute.pdf`
- All Python source files are empty stubs (0 bytes)
- Phase 1 plans created: 2 plans, 1 wave
- 10 test cases: 5 harmful (§1798.100, .105, .120, .125) + 5 safe
- Timeout: 120s per request, 300s startup wait
