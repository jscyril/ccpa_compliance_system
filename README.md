# Intelligent CCPA Compliance Analyzer

## Solution Overview

This system uses a **Retrieval-Augmented Generation (RAG)** architecture to analyze business practices against the California Consumer Privacy Act (CCPA) statute and return structured JSON verdicts. It is optimized for production workloads and integration with frontend systems.

### v2.0 Architecture (Gemini Engine)

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
            │  LLM Engine   │  ← Google Gemini API
            │  (Gemini 2.5) │  ← Fallback: gemini-2.0-flash
            └──────┬───────┘
                   │ JSON output (Standard or SSE Stream)
                   ▼
            ┌──────────────┐
            │Response Parser│  ← Validates 4-field schema
            │               │  ← Normalizes article format
            └──────┬───────┘
                   │
                   ▼
            {"harmful": bool, "articles": [...], "explanation": "...", "referenced_articles": [...]}
```

### Key Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM** | `gemini-2.5-pro` | Powerful cloud-based legal reasoning. Falls back to `gemini-2.0-flash` if Pro is unavailable or rate-limited. |
| **Embedder** | `BAAI/bge-small-en-v1.5` (CPU) | Embeds CCPA subsections into vectors for semantic retrieval. |
| **Vector DB** | ChromaDB (in-memory) | Stores and searches 212 embedded CCPA subsections at startup. |
| **API** | FastAPI + Uvicorn | Exposes `POST /analyze`, `GET /analyze/stream`, and `GET /health`. |
| **Knowledge Base** | `ccpa_sections.json` | Pre-parsed, hierarchically structured CCPA statute. |

### Processing Pipeline

1. **Preprocessing (build-time):** The verified `ccpa_statute.md` is parsed into `ccpa_sections.json` with hierarchical section → subsection structure.
2. **Startup:** The FastAPI server initializes. The embedding model (`bge-small`) indexes all 212 subsections into the ChromaDB collection.
3. **Inference:** For each prompt, the top-5 most relevant CCPA subsections are retrieved via semantic search, injected into a strict few-shot prompt, and sent to Google Gemini. 
4. **Safety Fallback:** If parsing fails or the LLM is uncertain, the system safely returns `{"harmful": false, "articles": []}` to avoid citing incorrect articles.

---

## Docker Deployment

The application is containerized in a lightweight `<200MB` Alpine/Slim image, designed for serverless environments (Google Cloud Run, Railway, Render). It uses a CPU-only architecture for embeddings and relies on the Gemini API for inference.

```bash
docker build -t ccpa-analyzer:latest .
docker run -p 8000:8000 -e GEMINI_API_KEY=<your_api_key> -e API_KEY=<optional_security_key> ccpa-analyzer:latest
```

> **Note:** The `bge-small` embedding model is pre-cached during the build phase (`docker build`) so container startup is extremely fast. The `GET /health` endpoint returns HTTP 200 when ready.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | **Yes** | Google Gemini API key. Obtained from Google AI Studio. |
| `API_KEY` | No | If set, the `/analyze` and `/analyze/stream` endpoints will require an `X-API-Key` header matching this value. |
| `CORS_ORIGINS` | No | Commma-separated list of allowed CORS origins (default: `*`). |
| `LLM_FALLBACK_MODE` | No | Set to "true" to force the use of `gemini-2.0-flash` over Pro. |

---

## API Usage Examples

> If the `API_KEY` environment variable is set on the server, you must include the `-H "X-API-Key: <your_key>"` header in all analysis requests.

### GET /health

Check if the API and vector database are ready.

**Request:**
```bash
curl http://localhost:8000/health
```

**Response (HTTP 200):**
```json
{"status": "healthy"}
```

---

### POST /analyze (Standard Request)

Analyze a business practice and receive a complete JSON payload.

**Request:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "We sell customer browsing history to ad networks without providing any opt-out mechanism."}'
```

**Response:**
```json
{
  "harmful": true,
  "articles": [
    "Section 1798.120"
  ],
  "explanation": "The CCPA grants consumers the right to direct a business that sells their personal information to third parties not to sell the consumer's personal information. Selling browsing history without an opt-out mechanism explicitly violates this right.",
  "referenced_articles": [
    "Section 1798.120(a) A consumer shall have the right, at any time, to direct a business that sells personal information about the consumer to third parties not to sell the consumer's personal information. This right may be referred to as the right to opt-out."
  ]
}
```

---

### GET /analyze/stream (SSE Streaming)

Stream the analysis response directly to a frontend as Server-Sent Events (SSE). This dramatically reduces perceived latency, especially for the `explanation` field generation.

**Request:**
```bash
curl -N "http://localhost:8000/analyze/stream?prompt=We%20sell%20customer%20browsing%20history."
```

**Response (Event Stream):**
```text
data: {"text": "{\n"}

data: {"text": "  \"harmful\": true,\n"}

data: {"text": "  \"articles\": [\n"}

data: {"text": "    \"Section 1798.120\"\n"}

data: {"text": "  ],\n..."}
```

---

## Local Development Setup

To run the application locally without Docker:

```bash
# 1. Clone and enter the project
cd ccpa_compliance_system/backend

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
export GEMINI_API_KEY="AIzaSyYourKeyHere..."

# 5. Pre-process CCPA statute into JSON
python scripts/preprocess_ccpa.py

# 6. Start the FastAPI server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Running the Integration Test

A unified end-to-end integration and benchmark script is provided in `backend/scripts/test_integration.py`. Make sure your server is running on `localhost:8000` before executing:

```bash
cd backend
export API_KEY="your_api_key_if_set"
python scripts/test_integration.py
```