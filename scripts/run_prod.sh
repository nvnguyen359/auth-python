#!/bin/bash
# Chạy server FastAPI ở chế độ production (gunicorn + uvicorn workers)

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
WORKERS=${WORKERS:-4}

echo "Starting FastAPI server in production mode..."
gunicorn -w $WORKERS -k uvicorn.workers.UvicornWorker app.main:app --bind $HOST:$PORT
