# STATE.md — Project Memory

> Last updated: 2026-03-01T16:45:00+05:30

## Current Position
- **Phase**: Not started (implementation plan created, awaiting approval)
- **Task**: All GSD files synced with architecture decisions
- **Blocked**: Yes — need CCPA statute PDF added to `backend/app/data/ccpa_statute.pdf`

## Architecture Decisions (Summary)
- **LLM**: Llama 3.1 8B Instruct, 4-bit quantized via bitsandbytes
- **Embeddings**: BAAI/bge-small-en-v1.5 (sentence-transformers)
- **Vector DB**: ChromaDB in-memory
- **Retrieval**: Parent-document retrieval (embed subsections, retrieve full sections)
- **Prompting**: Few-shot (3 examples) + system prompt
- **Fallback**: Unparseable/low-confidence output → `{"harmful": false, "articles": []}`
- **PDF parsing**: PyMuPDF (fitz)

## Session Context
- Codebase mapped via `/map` — `ARCHITECTURE.md` and `STACK.md` exist
- All Python source files are empty stubs (0 bytes)
- `main.py` entry point does not exist yet
- `ccpa_sections.json` is empty — needs CCPA PDF extraction
- CCPA statute PDF is **not yet in the repo**
- Docker files (`Dockerfile`, `startup.sh`) are empty stubs
- 10 test cases: 5 harmful (§1798.100, .105, .120, .125) + 5 safe
- Timeout: 120s per request, 300s startup wait

## Files Modified This Session
- `.gsd/SPEC.md` — Created (FINALIZED)
- `.gsd/REQUIREMENTS.md` — Created (10 requirements)
- `.gsd/ROADMAP.md` — Created and updated with tech choices
- `.gsd/DECISIONS.md` — Created (5 ADRs)
- `.gsd/STATE.md` — Created
- `.gsd/JOURNAL.md` — Created
- `.gsd/TODO.md` — Created
