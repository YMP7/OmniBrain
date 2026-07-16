#!/bin/bash

# Initialize the SQLite Database
python init_db.py

# Start FastAPI backend (which also serves the React frontend statically)
export PORT="${PORT:-8080}"
uvicorn api:app --host 0.0.0.0 --port $PORT
