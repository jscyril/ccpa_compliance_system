FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ app/
COPY scripts/ scripts/

# Pre-generate CCPA sections JSON during build
RUN python scripts/preprocess_ccpa.py

# Pre-download embedding model during build (~130MB, cached in layer)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"

# HF_TOKEN for model access (build-time for pre-download, runtime for loading)
ARG HF_TOKEN
ENV HF_TOKEN=${HF_TOKEN}

# Pre-download LLM tokenizer during build (model weights downloaded at runtime)
RUN if [ -n "$HF_TOKEN" ]; then \
    python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('meta-llama/Llama-3.1-8B-Instruct', token='${HF_TOKEN}')"; \
    fi

# Copy startup script
COPY startup.sh .
RUN chmod +x startup.sh

EXPOSE 8000

CMD ["bash", "startup.sh"]
