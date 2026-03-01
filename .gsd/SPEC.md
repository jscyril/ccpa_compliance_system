# SPEC.md — Project Specification

> **Status**: `FINALIZED`

## Vision
A high-performance FastAPI service that uses an under-8B parameter local LLM to automatically analyze short natural-language descriptions of business practices against the provided CCPA statute (PDF format), strictly returning whether the practice is harmful and which specific CCPA articles it violates as formatted JSON.

## Goals
1. Accurately classify data practices against the CCPA legal text.
2. Output a strictly typed JSON response (`harmful` boolean, `articles` list of strings).
3. Operate efficiently with low latency to pass automated test scripts.
4. Run entirely within a self-contained Docker image requiring only a Hugging Face token.

## Non-Goals (Out of Scope)
- Complex conversational interactions or chat history.
- Explaining the legal reasoning back to the caller (only strict JSON output is permitted).
- Models larger than 8 billion parameters.
- Hardcoding sensitive credentials like `HF_TOKEN`.

## Users
Automated evaluation scripts (`test.py`) that will rapidly send prompts and validate the JSON schema and correctness.

## Constraints
- **Technical**: Must run a local model (up to 8B params) via a Hugging Face token (passed strictly via `HF_TOKEN` environment variable).
- **Interface**: Must present a FastAPI HTTP server.
- **Environment**: Must be fully containerized via Docker.
- **Performance**: Must meet strict latency requirements for automated test evaluation.
- **Input/Knowledge Base**: Legal reasoning must be grounded in the provided CCPA statute PDF.

## Success Criteria
- [ ] Successfully builds into a Docker image.
- [ ] Container accepts `HF_TOKEN` environment variable and downloads/initializes the model.
- [ ] FastAPI server starts and accepts queries.
- [ ] Returns exactly the `{"harmful": true | false, "articles": ["Section 1798.xxx"]}` schema.
- [ ] Zero extra text, markdown formatting, or explanation in the output.
- [ ] Passes whatever automated `test.py` script the evaluation framework uses within the latency limits.
