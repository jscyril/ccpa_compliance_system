# Intelligent CCPA Compliance Analyzer

An automated system that reads a description of a company's data handling behavior, reasons over the California Consumer Privacy Act (CCPA) statute, and instantly flags potential violations along with specific statute sections.

## Solution Overview

This system utilizes a **Retrieval-Augmented Generation (RAG)** architecture to overcome the token limits and reasoning constraints of smaller LLMs. 

1. **Knowledge Base Generation**: The raw `ccpa_statute.pdf` is pre-parsed into structured sections and subsections to preserve legal hierarchy.
2. **Embedding & Retrieval**: A lightweight embedding model (`BAAI/bge-small-en-v1.5`) runs on the CPU. It vectorizes the CCPA subsections into a ChromaDB in-memory index. Given a user prompt, it retrieves the top functionally relevant subsections.
3. **Prompt Construction**: The retrieved sections are truncated to fit the context window, combined with 3 few-shot examples (2 harmful, 1 safe), and formatted into a strict Llama 3.2 Instruct system prompt.
4. **LLM Inference**: The 3B parameter `meta-llama/Llama-3.2-3B-Instruct` model analyzes the prompt and output strictly formatted JSON. Greedy decoding (`do_sample=False`) is used to mathematically guarantee deterministic, structured output and prevent numerical instability (NaN values).
5. **Robust Parsing**: The output is parsed into a strict JSON schema. If the LLM generates trailing or conversational text, a fallback regex parser extracts the JSON. If the LLM entirely fails, a "safe by default" ADR-4 fallback returns `{"harmful": false, "articles": []}`.

## Docker Run Instructions

To pull and run the container locally:

```bash
docker run --gpus all -p 8000:8000 -e HF_TOKEN=<your_huggingface_token> yourusername/ccpa-compliance:latest
```

*Note: The `--gpus all` flag allows the container to use an NVIDIA GPU if present. The system automatically falls back to CPU float16 if no CUDA device is detected, but CPU inference requires ~16GB of RAM allocated to Docker.*

## Environment Variables

| Variable | Description | Requirement |
|----------|-------------|-------------|
| `HF_TOKEN` | Hugging Face access token for gated/open models (e.g., Llama-3.2-3B). Essential for downloading model weights at startup. | Required |

## GPU Requirements & Fallback

- **Minimum GPU VRAM**: 8GB (ideal for 3B parameter models in float16)
- **CPU Fallback**: Full support for CPU-only instances. If no GPU is present, the app automatically transitions to standard PyTorch CPU execution using float16.
- **Apple Silicon (MPS)**: Natively supported outside Docker. Tests show MPS reduces latency significantly. If MPS is available, float32 is used to avoid Metal-specific NaN numeric instability.

## API Usage Examples

The FastAPI server exposes two endpoints.

### 1. GET `/health`
Check if the models are loaded and the vector index is built.

**Request:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{"status": "ok", "vector_store_ready": true, "llm_ready": true}
```

### 2. POST `/analyze`
Analyze a business practice for CCPA violations.

**Request (Harmful Case):**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "We sell customer browsing history to ad networks without notifying them."}'
```

**Response:**
```json
{
  "harmful": true,
  "articles": [
    "Section 1798.100",
    "Section 1798.120"
  ]
}
```

**Request (Safe Case):**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"prompt": "We provide a clear privacy policy and honor all deletion requests."}'
```

**Response:**
```json
{
  "harmful": false,
  "articles": []
}
```

## Local Setup Instructions (Fallback)

If Docker fails, you can run the application directly on a Linux VM.

**1. Prerequisites:**
Ensure you have Python 3.11+ installed.
```bash
sudo apt update && sudo apt install -y python3.11 python3.11-venv build-essential
```

**2. Setup Virtual Environment:**
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Pre-process CCPA Data:**
```bash
export HF_TOKEN=<your_huggingface_token>
python scripts/preprocess_ccpa.py
```

**4. Start the Server:**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 300
```

Wait until you see `SERVER READY` in the terminal logs before sending requests.