#!/bin/bash
# Initialize DB
python backend/init_db.py

# Start the unified backend
export PORT="${PORT:-8080}"
uvicorn backend.api:app --host 0.0.0.0 --port $PORT
