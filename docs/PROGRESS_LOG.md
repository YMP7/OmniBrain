# OmniBrain — Progress Log

This file is the human-readable mirror of the `project_status` database table described in
`OmniBrain_Memory_and_State_Management.md` (Section 4). Newest entries appear at the top.

---

### 2026-07-16 (Implementation Start)
- [DONE] End-to-End Validation (`test_e2e.py`) passed. Wrote automated Playwright tests to validate the Streamlit UI loading with injected CSS and verified graceful failure behavior when the API key is omitted.
- [DONE] Streamlit UI (`app.py`) completed. Applied Taste Skills (`emilkowal.ski`, `impeccable.style`) directly via custom CSS injection (dark mode, Inter font, minimal bento-grids).
- [DONE] FastAPI Gateway (`api.py`) completed. Exposes `/upload` and `/query`.
- [DECISION] Frontend Dependencies: Added `motion/react` to enable reduced-motion aware, physical spring animations for the new React bento UI. This is a deliberate, minimal addition to the dependency graph, consistent with the Ponytail philosophy (avoiding heavy alternatives like Framer Motion or unneeded wrappers).
- [DECISION] Guardrails: NeMo guardrails and Langfuse observability are explicitly skipped for this MVP phase in strict adherence to Ponytail's minimal dependency/YAGNI philosophy. This is a known scope reduction. Instead, a minimal grounding/citation check is hardcoded directly into the Supervisor's synthesize step (`supervisor.py`) which rejects/flags responses lacking `[Source: X, Page: Y]` citations.
- [DONE] Agentic Orchestrator (LangGraph Supervisor) implemented (`supervisor.py`). Built a minimal StateGraph mapping routing logic between our Search, SQL, and Vision agents via an LLM.
- [DECISION] Table Extraction: Since Camelot is skipped, tables and vector-drawn charts will be processed by rendering entire PDF pages as high-res images (`page.get_pixmap()`). The Vision Agent will read and extract tabular data visually via the VLM.
  - *KNOWN GAP*: Rendering every page as an image won't scale well to 500-page use cases. Page-image rendering should eventually be limited to pages explicitly containing images/drawings.
- [DONE] Specialized Agents (Search, SQL, Vision) implemented (`agents.py`) in a single modular file to avoid boilerplate, completely adhering to Ponytail.
- [DONE] Ingestion Pipeline implemented (`ingestion.py`) with bare-minimum Langchain text chunking and FAISS embeddings, rejecting heavy OCR dependencies per Ponytail.
- [DONE] Provisioned local SQLite DB (`omnibrain.db`) to serve as relational data store, explicitly rejecting PostgreSQL to satisfy Ponytail's minimal dependency rule.
- [DONE] Installed FAISS (`faiss-cpu`) to serve as local in-memory vector storage, explicitly rejecting Qdrant to satisfy Ponytail's minimal dependency rule.

### 2026-07-16
- [DONE] Architecture design finalized — `OmniBrain_Architecture.md` covers system overview, workflow, and key technologies.
- [DONE] Agent role specs written — Supervisor, Search, SQL, and Vision agent docs completed with responsibilities, implementation details, and example workflows.
- [DONE] Skills & tooling catalogue defined — `OmniBrain_Skills_and_Tooling.md` lists parsing, retrieval, reasoning, and guardrail tools/technologies to be used.
- [DONE] Memory & state management design finalized, including this Progress Ledger mechanism (module + task-level tracking).
- [NOT STARTED] No implementation code written yet for any module (ingestion pipeline, Supervisor/Search/SQL/Vision agents, guardrails, UI, or API gateway).
- [NOT STARTED] Vector DB (Qdrant/FAISS) and relational DB (PostgreSQL/MySQL) not yet provisioned.
- [NOT STARTED] Langfuse and NeMo Guardrails not yet integrated.

**Overall status:** Planning & design phase complete for Project 1 (OmniBrain). Ready to begin implementation.
