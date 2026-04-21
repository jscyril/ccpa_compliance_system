#!/bin/bash
set -e

# Default to port 8080 if PORT is not set
export PORT="${PORT:-8080}"

echo "=========================================="
echo " CCPA Compliance Analyzer"
echo "=========================================="

# ── Validate required configuration ──────────────────────────
if [ -z "$GEMINI_API_KEY" ]; then
    echo ""
    echo "  [ERROR] GEMINI_API_KEY is not set!"
    echo ""
    echo "  You must provide your Google Gemini API key."
    echo "  Get one at: https://aistudio.google.com/apikey"
    echo ""
    echo "  Usage:"
    echo "    docker run -p 8080:8080 \\"
    echo "      -e GEMINI_API_KEY=your_key_here \\"
    echo "      -e GEMINI_MODEL=gemini-2.0-flash \\"
    echo "      ccpa-compliance-analyzer:latest"
    echo ""
    exit 1
fi

echo "  Port:       $PORT"
echo "  Model:      ${GEMINI_MODEL:-gemini-2.0-flash}"
echo "  API Key:    ${GEMINI_API_KEY:0:8}...****"
echo "=========================================="

# Substitute the PORT variable into the nginx config template
envsubst '${PORT}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf

# Start the backend (uvicorn) in the background
echo "[1/2] Starting backend (uvicorn on :8000)..."
cd /app/backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "[INFO] Waiting for backend to be ready..."
for i in $(seq 1 60); do
    if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
        echo "[INFO] Backend is healthy!"
        break
    fi
    sleep 2
done

# Start nginx in the foreground
echo "[2/2] Starting nginx on :$PORT..."
nginx -g "daemon off;" &
NGINX_PID=$!

# Trap signals and forward to both processes
trap "kill $BACKEND_PID $NGINX_PID; exit 0" SIGTERM SIGINT

# Wait for either process to exit
wait -n $BACKEND_PID $NGINX_PID
EXIT_CODE=$?
kill $BACKEND_PID $NGINX_PID 2>/dev/null || true
exit $EXIT_CODE
