# OmniBrain: QA & Project Completion Report

## 1. Architecture Summary (What was built)
OmniBrain is a multimodal, multi-agent financial document analysis system built on a unified FastAPI + React architecture.
- **Frontend**: A minimal, dark-themed React application (`frontend/`) built with Vite, Tailwind v4, and Phosphor Icons, utilizing `motion/react` for reduced-motion aware bento-card animations. Served statically via FastAPI in production.
- **API Gateway**: A FastAPI backend (`api.py`) exposing two core routes (`/upload` and `/query`).
- **Ingestion**: `ingestion.py` chunks text and uses a local FAISS CPU index for dense embeddings. Document pages are also rendered into full-page high-res images (`.png`) for the Vision Agent.
- **Orchestration**: `supervisor.py` uses LangGraph to coordinate routing between specialized agents. It maintains a state variable (`intermediate_findings`) using `operator.add` to accumulate insights across multiple agent iterations.
- **Agents**: Defined in `agents.py`:
  - **Search Agent**: Queries the local FAISS vector store.
  - **SQL Agent**: Queries the local SQLite (`omnibrain.db`) relational database.
  - **Vision Agent**: Analyzes the rendered `.png` pages using GPT-4o's multimodal capabilities to extract tabular and chart data.

## 2. Test Coverage & Verification
**What `test_e2e.py` verifies:**
- **UI Rendering:** Playwright ensures the React DOM renders the correct bento-grid layouts (Ingestion Panel, Query Panel, Findings Display).
- **Graceful Failure:** The UI properly displays an inline error component (e.g. `"Query failed: Internal Server Error"`) without crashing if the backend returns a 500 status code (such as when the API key is missing).
- **State Accumulation & Citations (Mocked):** The backend is mocked to intercept OpenAI calls. It verifies that `supervisor.py` successfully aggregates findings from *multiple* agents into `intermediate_findings`, and that the strict `[Source: X, Page: Y]` citation check enforces properly formatted citations in the final synthesized output.
- **Backend Error Handling:** The `/upload` route correctly catches backend ingestion failures (e.g. missing `OPENAI_API_KEY` or file parsing errors) by surfacing a strict HTTP 500 error, instead of silently suppressing exceptions and returning a false success message.

**What is NOT yet verified:**
- **A real, non-mocked GPT-4o run.** While the integration code is confirmed to successfully dial out to the live OpenAI API, testing is currently blocked by an `HTTP 429 Insufficient Quota` billing error on the provided API key. The real LLM reasoning behavior and vision parsing quality remain pending until a funded key is supplied.

## 3. Known Scope Reductions & Rationale
To strictly adhere to a minimal-dependency, YAGNI philosophy, the following architectural choices were made:
- **Vector Storage**: Used local in-memory `faiss-cpu` instead of standing up a heavy Qdrant server.
- **Relational Storage**: Used local `SQLite` (`omnibrain.db`) instead of PostgreSQL.
- **Table Extraction**: Dropped heavy OCR dependencies (like Camelot/Ghostscript) in favor of rendering entire PDF pages to images for the VLM (Vision Agent) to interpret directly.
- **Guardrails**: Deferred NeMo Guardrails and Langfuse observability. Instead, a lightweight manual grounding guard is hardcoded in the supervisor's synthesis step, ensuring responses without source/page citations are flagged.

## 4. Known Limitations
- **Cloud Run Deployment**: Deferred. A local `deploy.sh` script is provided, but it has not been executed or wired into a CI/CD pipeline (e.g., Cloud Build).
- **Ephemeral Storage**: If deployed to Cloud Run as-is, the local `omnibrain.db` and FAISS index will be ephemeral. Restarting the container will wipe the uploaded knowledge base.
- **Scaling**: Must be deployed with `--max-instances=1` to prevent state fragmentation across multiple stateless containers.
- **Rate Limiting**: No API rate limiting is implemented; exposing this publicly without an API Gateway or middleware could quickly exhaust OpenAI quotas.

## 5. Recommended Next Steps
In its current state, OmniBrain is a **complete, demoable portfolio project**. Before it can be considered "production ready" for a multi-user environment, the following steps are recommended:
1. **Persistent Storage:** Migrate SQLite to Cloud SQL (PostgreSQL) and FAISS to a managed vector database (e.g., Pinecone or Qdrant Cloud).
2. **Quota Verification:** Rerun `test_e2e.py` (or `run_real_query.py`) with a funded OpenAI API key to tune the multi-agent system prompts based on real GPT-4o responses.
3. **Deployment Pipeline:** Configure a `cloudbuild.yaml` to build the multi-stage Docker image and continuously deploy it to Cloud Run.
