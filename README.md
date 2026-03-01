# Intelligent CCPA Compliance Analyzer

## Solution Overview

This system uses a **Retrieval-Augmented Generation (RAG)** architecture to analyze business practices against the California Consumer Privacy Act (CCPA) statute and return structured JSON verdicts.

### Architecture

```
User Prompt ──► FastAPI (/analyze)
                    │
                    ▼
            ┌──────────────┐
            │ Vector Search │  ← ChromaDB (in-memory)
            │ (bge-small)   │  ← Embeds 212 CCPA subsections
            └──────┬───────┘
                   │ Top-5 relevant statute sections
                   ▼
            ┌──────────────┐
            │Prompt Builder │  ← System prompt + few-shot examples
            │               │  ← Retrieved CCPA context injected
            └──────┬───────┘
                   │ Structured prompt
                   ▼
            ┌──────────────┐
            │  LLM Engine   │  ← Dual-model with 90s timeout
            │  (Reasoning)  │  ← Primary: DeepSeek-R1-8B
            │               │  ← Fallback: Phi-4-mini-reasoning
            └──────┬───────┘
                   │ Raw text output
                   ▼
            ┌──────────────┐
            │Response Parser│  ← Strips <think> tags
            │               │  ← Extracts & validates JSON
            │               │  ← Normalizes article format
            └──────┬───────┘
                   │
                   ▼
            {"harmful": bool, "articles": [...]}
```

### Key Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM (Primary)** | `deepseek-ai/DeepSeek-R1-Distill-Llama-8B` | Best reasoning model. Runs with a 90-second timeout per request. |
| **LLM (Fallback)** | `microsoft/Phi-4-mini-reasoning` | Faster 3.8B reasoning model. Activated automatically if the primary times out or fails. |
| **Embedder** | `BAAI/bge-small-en-v1.5` (CPU) | Embeds CCPA subsections into vectors for semantic retrieval. |
| **Vector DB** | ChromaDB (in-memory) | Stores and searches 212 embedded CCPA subsections at startup. |
| **API** | FastAPI + Uvicorn | Exposes `POST /analyze` and `GET /health` on port 8000. |
| **Knowledge Base** | `ccpa_statute.md` → `ccpa_sections.json` | Pre-parsed, hierarchically structured CCPA statute (45 sections, 212 subsections). |

### Processing Pipeline

1. **Preprocessing (build-time):** The verified `ccpa_statute.md` is parsed into `ccpa_sections.json` with hierarchical section → subsection structure.
2. **Startup:** Both LLMs are loaded (4-bit quantized on GPU, float16 on CPU, float32 on MPS). The embedding model indexes all 212 subsections into ChromaDB.
3. **Inference:** For each prompt, the top-5 most relevant CCPA subsections are retrieved via semantic search, injected into a few-shot prompt, and passed to the **primary model** (DeepSeek-R1-8B) with a 90-second timeout. If the primary model times out or fails, the prompt is automatically retried with the **fallback model** (Phi-4-mini-reasoning). The output is stripped of `<think>` tags and parsed into strict JSON.
4. **Safety Fallback:** If parsing fails or the LLM is uncertain, the system returns `{"harmful": false, "articles": []}` to avoid citing incorrect articles.

---

## Docker Run Command

```bash
docker run --gpus all -p 8000:8000 -e HF_TOKEN=<your_huggingface_token> yourusername/ccpa-compliance:latest
```

> **Note:** The container starts, loads the LLM, and builds the vector index during startup. The `GET /health` endpoint will return HTTP 200 once the server is fully ready. This may take up to 2–3 minutes depending on hardware.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `HF_TOKEN` | **Yes** | Hugging Face access token for downloading the gated DeepSeek-R1-8B and Phi-4-mini-reasoning model weights. Must be provided at runtime via `-e HF_TOKEN=<token>`. Never hardcoded in source code. |

---

## GPU Requirements

| Hardware | Strategy | VRAM/RAM Needed | Performance |
|----------|----------|-----------------|-------------|
| NVIDIA GPU (recommended) | 4-bit quantized (`bitsandbytes`) | **~8 GB VRAM** (both models) | ~5–10s per request |
| NVIDIA GPU (fallback) | float16 | ~24 GB VRAM | ~5–10s per request |
| CPU-only | float16 on CPU | ~24 GB RAM | ~60–90s per request |
| Apple Silicon (MPS) | float32 on Metal | ~24 GB unified RAM | ~15–30s per request |

- **Minimum GPU VRAM:** 8 GB (both models in 4-bit quantization)
- **CPU-only fallback:** Fully supported. If no CUDA GPU is detected, the system automatically falls back to CPU float16. This requires at least 24 GB of RAM allocated to the Docker container.

---

## Local Setup Instructions (Fallback)

If the Docker image fails to start, use these steps to run the system directly on a Linux VM.

### Prerequisites

- Python 3.11 or higher
- At least 24 GB RAM (for CPU inference with both models)
- A valid Hugging Face token with access to `deepseek-ai/DeepSeek-R1-Distill-Llama-8B` and `microsoft/Phi-4-mini-reasoning`

### Step-by-Step

```bash
# 1. Clone and enter the project
cd ccpa_compliance_system/backend

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set HF token
export HF_TOKEN=<your_huggingface_token>

# 5. Pre-process CCPA statute into JSON
python scripts/preprocess_ccpa.py

# 6. Start the FastAPI server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 300
```

Wait until `SERVER READY` appears in the logs before sending requests.

### Verify it works

```bash
# Health check
curl http://localhost:8000/health

# Test a harmful prompt
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "We sell customer browsing history to ad networks without notifying them."}'
```

---

## API Usage Examples

### GET /health

Check if the server is ready and all models are loaded.

**Request:**
```bash
curl http://localhost:8000/health
```

**Response (HTTP 200):**
```json
{"status": "ok", "vector_store_ready": true, "llm_ready": true}
```

---

### POST /analyze

Analyze a business practice for CCPA violations.

**Request — Violation Detected:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "We sell customer browsing history to ad networks without notifying them."}'
```

**Response:**
```json
{"harmful": true, "articles": ["Section 1798.100", "Section 1798.120"]}
```

**Request — No Violation:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "We provide a clear privacy policy and honor all deletion requests."}'
```

**Response:**
```json
{"harmful": false, "articles": []}
```

> ⚠ The response body contains **only valid JSON** — no extra text, no markdown, no explanation.