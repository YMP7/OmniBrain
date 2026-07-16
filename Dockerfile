# Stage 1: Build the React frontend
FROM node:20-slim AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build the Python backend
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies (for PyMuPDF/FAISS if needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Copy built frontend from stage 1
COPY --from=frontend-builder /frontend/dist /app/frontend/dist

# Ensure SQLite DB and test data paths are accessible
RUN chmod 777 /app

EXPOSE 8080

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
