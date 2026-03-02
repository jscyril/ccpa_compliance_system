FROM python:3.13-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install required system packages for building (e.g., ChromaDB)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy dependency file and install dependencies
# Doing this before copying code caches the dependencies layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and scripts
COPY app/ app/
COPY scripts/ scripts/

# Pre-generate CCPA sections JSON during the build process
RUN python scripts/preprocess_ccpa.py

# Pre-download the embedding model during build so it gets cached in the image layer
# This avoids downloading the ~130MB model at runtime
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"

# Expose the API port
EXPOSE 8000

# Run the FastAPI application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
