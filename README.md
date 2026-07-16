# OmniBrain — Agentic Multi-Modal RAG Orchestrator

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black" alt="React 18">
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/LangGraph-Orchestration-1C3C3C?style=flat-square" alt="LangGraph">
  <img src="https://img.shields.io/badge/GPT--4o-OpenAI-412991?style=flat-square&logo=openai&logoColor=white" alt="GPT-4o">
  <img src="https://img.shields.io/badge/Vite-Build-646CFF?style=flat-square&logo=vite&logoColor=white" alt="Vite">
  <img src="https://img.shields.io/badge/FAISS-Vector%20Store-4285F4?style=flat-square" alt="FAISS">
  <img src="https://img.shields.io/badge/SQLite-Relational%20DB-003B57?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite">
</p>

<p align="left">
  <img src="https://img.shields.io/badge/status-active%20development-yellow?style=flat-square" alt="Status: Active Development">
  <img src="https://img.shields.io/badge/tests-passing%20(mocked)-brightgreen?style=flat-square" alt="Tests: Passing (Mocked)">
  <img src="https://img.shields.io/badge/deployment-local%20only-lightgrey?style=flat-square" alt="Deployment: Local Only">
  <img src="https://img.shields.io/badge/license-all%20rights%20reserved-red?style=flat-square" alt="License: All Rights Reserved">
</p>

OmniBrain is a multi-agent system for answering complex questions over financial documents that mix unstructured text, structured data, and visual content (charts, tables, graphs). It uses a LangGraph-orchestrated supervisor to dynamically route sub-tasks to specialized agents, then synthesizes a single, cited answer grounded in the retrieved evidence.

**Example use case:** feed in a multi-page financial report PDF, then ask a question like *"What was the Q3 revenue growth in Asia Pacific, and does it match the chart in the presentation?"* — OmniBrain retrieves the relevant text, reads the actual chart image, cross-references structured data, and returns one answer with `[Source, Page]` citations for every claim.

---

## Architecture

```
User Query
    │
    ▼
┌─────────────────────┐
│  Supervisor Agent    │  LangGraph state machine — analyzes the query,
│  (supervisor.py)     │  routes to the right specialized agent(s), loops
└─────────┬────────────┘  until findings are sufficient (max 6 steps)
          │
    ┌─────┼─────┬─────────┐
    ▼     ▼     ▼         
┌───────┐ ┌───────┐ ┌────────┐
│Search │ │ SQL   │ │ Vision │
│Agent  │ │ Agent │ │ Agent  │
└───┬───┘ └───┬───┘ └───┬────┘
    │         │         │
    ▼         ▼         ▼
  FAISS    SQLite    GPT-4o Vision
 (text)   (queries)  (page images)
    │         │         │
    └─────────┼─────────┘
              ▼
     Synthesis + Citation
     Grounding Guard
              │
              ▼
        Final Answer
     (React frontend)
```

| Layer | Technology |
|---|---|
| Frontend | React + Vite, Tailwind, `motion/react` — served as static build via FastAPI |
| API Gateway | FastAPI (`/upload`, `/query`) |
| Orchestration | LangGraph (state machine, conditional routing, citation-grounded synthesis) |
| Vector Store | FAISS (local, in-memory) |
| Relational Store | SQLite |
| LLM / VLM | OpenAI GPT-4o (text reasoning, Text-to-SQL, vision) |
| PDF Ingestion | PyMuPDF (`fitz`) — text extraction + full-page rendering |

---

## Key Design Decisions

This project deliberately favors a **lean, dependency-minimal stack** over a "textbook enterprise" setup, on the principle that the value being demonstrated is the *agentic reasoning pipeline*, not infrastructure operations. Where the original design called for heavier tooling, a lighter substitute was used instead:

| Originally considered | Used instead | Why |
|---|---|---|
| Qdrant (vector DB) | FAISS (in-memory) | No server to run/maintain for a single-user local system |
| PostgreSQL | SQLite | Zero setup, file-based, sufficient for structured demo data |
| Camelot / Tesseract (table & OCR extraction) | Full-page rendering to the Vision Agent | Vector-drawn charts and complex tables are notoriously brittle to parse structurally; rendering the whole page and letting GPT-4o read it visually is more robust and avoids a whole class of fragile dependencies |
| NeMo Guardrails + Langfuse | A custom citation-enforcement check in the Supervisor's synthesis step | Full observability/guardrails tooling was out of scope for an MVP; a lightweight rule — every factual claim must carry a `[Source, Page]` citation, or the response is rejected — captures the core hallucination-prevention goal directly |

These substitutions are documented in detail, along with the full build history, in [`docs/PROGRESS_LOG.md`](docs/PROGRESS_LOG.md) and [`QA_REPORT.md`](QA_REPORT.md).

---

## Project Structure

```
OmniBrain/
├── README.md
├── QA_REPORT.md              # Test coverage, known gaps, scope rationale
├── requirements.txt
├── Dockerfile                 # Multi-stage: builds React, then Python runtime
├── start.sh                   # DB init + uvicorn entrypoint
├── .env.example                # Required environment variables (no real values)
│
├── docs/                      # Architecture & design documentation
│   ├── OmniBrain_Architecture.md
│   ├── OmniBrain_Memory_and_State_Management.md
│   ├── OmniBrain_Skills_and_Tooling.md
│   ├── Supervisor_Agent.md
│   ├── Search_Agent.md
│   ├── SQL_Agent.md
│   ├── Vision_Agent.md
│   └── PROGRESS_LOG.md        # Chronological build/status log
│
├── backend/                   # Python source
│   ├── api.py                 # FastAPI app: /upload, /query, static file serving
│   ├── supervisor.py           # LangGraph state machine & routing logic
│   ├── agents.py               # Search / SQL / Vision agent implementations
│   ├── ingestion.py             # PDF parsing, chunking, embedding, page rendering
│   ├── init_db.py               # SQLite schema + progress-ledger seed data
│   └── project_status_seed.sql
│
├── frontend/                  # React + Vite single-page app
│   └── src/
│       ├── App.tsx
│       └── components/
│           ├── IngestionPanel.tsx
│           ├── QueryPanel.tsx
│           └── FindingsDisplay.tsx
│
└── tests/
    ├── test_e2e.py             # Playwright UI + functional backend tests
    └── generate_test_pdf.py    # Generates a sample multi-page financial PDF
```

---

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+ (for the frontend build)
- An OpenAI API key with available quota

### 1. Clone and configure environment

```bash
git clone <this-repo>
cd OmniBrain
cp .env.example .env
# Edit .env and set OPENAI_API_KEY — never commit this file
```

### 2. Backend setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python backend/init_db.py        # Initializes SQLite schema + progress ledger
```

### 3. Frontend setup

```bash
cd frontend
npm install
npm run build                    # Produces frontend/dist, served by FastAPI
cd ..
```

### 4. Run

```bash
export OPENAI_API_KEY="sk-..."   # Windows: $env:OPENAI_API_KEY="sk-..."
uvicorn backend.api:app --host 0.0.0.0 --port 8080
```

Visit `http://localhost:8080` — FastAPI serves both the API and the built React frontend on a single port.

### 5. Try it out
1. Upload a PDF via the Ingestion panel (or use `tests/generate_test_pdf.py` to create a sample).
2. Ask a question in the Query panel that spans multiple data types, e.g. *"What was the revenue growth shown in the chart, and how does it compare to the database figures?"*
3. The response includes `[Source: filename, Page: N]` citations for every factual claim.

---

## Testing

```bash
python tests/test_e2e.py
```

This runs Playwright-driven UI tests (rendering, error states) plus a backend functional test verifying multi-agent state accumulation and citation enforcement. See [`QA_REPORT.md`](QA_REPORT.md) for exactly what is and isn't covered — notably, full end-to-end verification with a live (non-mocked) GPT-4o call is currently pending available OpenAI quota.

---

## Known Limitations

- **Local storage only.** SQLite and FAISS live on local disk — this is intentional for a single-user demo, but means state does not persist across container restarts if deployed, and does not scale across multiple instances without migrating to managed storage (Cloud SQL, a hosted vector DB).
- **No rate limiting.** The `/query` and `/upload` endpoints have no throttling; exposing this publicly without additional middleware risks unexpected OpenAI usage costs.
- **Deployment is deferred.** A `Dockerfile` and deploy script exist and were validated for structure, but Cloud Run deployment itself is currently out of scope by design — see `QA_REPORT.md`.

## Roadmap / Next Steps

- Verify real (non-mocked) GPT-4o reasoning quality once OpenAI quota is available.
- Migrate to managed storage (Cloud SQL + a hosted vector DB) if moving beyond single-instance local use.
- Add basic rate limiting before any public deployment.
- Extend the Progress Ledger pattern to Projects 2 and 3 of this portfolio series.

---

## License

This is a personal portfolio project. No license is currently specified — all rights reserved unless otherwise stated.
