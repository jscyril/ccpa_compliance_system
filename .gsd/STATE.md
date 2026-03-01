# STATE.md — Project Memory

> Last updated: 2026-03-01T16:36:00+05:30

## Current Position
- **Phase**: Not started
- **Task**: Project initialization complete
- **Blocked**: No

## Session Context
- Codebase mapped via `/map` — `ARCHITECTURE.md` and `STACK.md` exist
- All Python source files are empty stubs (0 bytes)
- `main.py` entry point does not exist yet
- `ccpa_sections.json` is empty — needs CCPA PDF extraction
- CCPA statute PDF is expected at `iisc_openHack_package/ccpa_hackathon_package/ccpa_statute.pdf` but no PDF currently in repo
- Docker files (`Dockerfile`, `startup.sh`) are empty stubs

## Key Decisions
- Model must be ≤8B parameters, loaded via HuggingFace Transformers
- `HF_TOKEN` passed as env var, never hardcoded
- Output schema: `{"harmful": true|false, "articles": ["Section 1798.xxx", ...]}`
- 10 test cases: 5 harmful (violations of §1798.100, .105, .120, .125) + 5 safe
- Timeout: 120s per request, 300s startup wait
