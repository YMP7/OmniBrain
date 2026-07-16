# OmniBrain

OmniBrain is a multimodal, multi-agent financial document analysis system built on a unified FastAPI + React architecture.

## Architecture & Scope Decisions
OmniBrain utilizes a minimal-dependency, "Ponytail" philosophy approach:
- **Vector Storage**: Local in-memory FAISS CPU index instead of heavier alternatives like Qdrant.
- **Relational DB**: Local SQLite (`omnibrain.db`) instead of PostgreSQL.
- **Table/Chart Extraction**: Direct full-page image rendering for the Vision Agent (VLM) rather than relying on heavy OCR/table extraction dependencies.
- **Orchestration**: A LangGraph `supervisor` routes queries between the Semantic Search, SQL, and Vision agents.
- **Guardrails**: Custom citation-based grounding checks instead of external guardrail frameworks.

For full architectural details, see the documentation in [`docs/`](docs/).

## Local Setup

### 1. Environment Variables
Copy `.env.example` to `.env` and fill in your OpenAI API Key (required for embeddings, GPT-4o, and Vision LLM reasoning):
```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY
```

### 2. Backend Setup
Create a virtual environment and install Python dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # Or `.venv\Scripts\Activate.ps1` on Windows
pip install -r requirements.txt
```

### 3. Frontend Setup
Install Node dependencies and build the static frontend (which FastAPI will serve):
```bash
cd frontend
npm install
npm run build
cd ..
```

## Running the Application
OmniBrain uses a unified backend that serves the static React frontend from the root path (`/`).

Simply run the provided startup script:
```bash
./start.sh
# Or run manually:
# python backend/init_db.py
# uvicorn backend.api:app --host 0.0.0.0 --port 8080
```
Then navigate to `http://localhost:8080` in your browser.

## Testing
Run the comprehensive E2E validation script which covers React UI rendering, graceful failure handling, and state accumulation (using a mocked backend):
```bash
python tests/test_e2e.py
```
*(Requires a dummy PDF generated via `python tests/generate_test_pdf.py`)*
