#!/bin/bash
set -e

# Default to port 10000 (Render's default) if PORT is not set
export PORT="${PORT:-10000}"

echo "=========================================="
echo " CCPA Compliance Analyzer"
echo " Starting on port $PORT"
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
