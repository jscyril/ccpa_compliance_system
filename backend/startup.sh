#!/bin/bash
set -e

echo "Starting CCPA Compliance Analyzer..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --timeout-keep-alive 300 \
    --workers 1
