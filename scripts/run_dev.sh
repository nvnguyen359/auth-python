# Chạy server dev (uvicorn) 
#!/bin/bash
# Chạy server FastAPI bằng uvicorn

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}

echo "Starting FastAPI server on $HOST:$PORT ..."
uvicorn app.main:app --host $HOST --port $PORT --reload
