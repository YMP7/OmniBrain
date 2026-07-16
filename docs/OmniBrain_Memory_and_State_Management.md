# OmniBrain: Memory and State Management

Effective memory and state management are crucial for OmniBrain to maintain context, track progress, and enable multi-turn interactions and complex reasoning across its agentic workflow. This document details how OmniBrain handles conversational memory and the internal state of its agents.

## 1. Conversational Memory

Conversational memory allows the OmniBrain system to remember past interactions with the user, providing context for subsequent queries and enabling more natural and coherent dialogues. This is particularly important for follow-up questions or when the user refers back to previous information.

### Implementation:

*   **Short-Term Memory (Context Window):** For immediate conversational context, the most recent turns of the conversation (user queries and agent responses) are maintained within the LLM's context window. This allows the LLM to understand the current query in light of recent dialogue.
*   **Long-Term Memory (Vector Database):** For more persistent and extensive memory, key conversational turns, extracted facts, and agent findings can be summarized and embedded into the vector database. This allows the system to retrieve relevant past information even after it has fallen out of the short-term context window.
*   **Session Management:** Each user interaction session is assigned a unique ID. All conversational history and intermediate states are associated with this session ID, allowing users to resume conversations or refer to past interactions.

## 2. Agent State Management

Within the LangGraph framework, the state of the entire agentic system is explicitly managed. This state object is passed between nodes (agents/functions) and updated at each step, providing a clear and auditable trace of the workflow.

### Key State Components:

*   **User Query:** The original query submitted by the user.
*   **Conversation History:** A list of past user inputs and agent outputs.
*   **Intermediate Findings:** Results returned by specialized agents (Search, SQL, Vision) at each step of the reasoning process.
*   **Routing Decisions:** The decisions made by the Supervisor Agent regarding which specialized agent to invoke next.
*   **Tool Calls:** Records of which tools (e.g., database queries, VLM calls) were executed and their outcomes.
*   **Self-Correction Attempts:** Information about when and how agents attempted to self-correct (e.g., rewriting a search query).
*   **Citations:** References to the source documents or data points used to generate parts of the response.

### State Persistence:

*   **LangGraph State:** LangGraph inherently manages the state transitions. For persistence across longer sessions or system restarts, the state can be serialized and stored in a database (e.g., Redis, PostgreSQL) or a dedicated state management service.
*   **Langfuse Integration:** Langfuse plays a crucial role in observing and persisting the execution traces, including the state changes and intermediate steps of the agents. This provides a detailed audit trail for debugging, evaluation, and understanding agent behavior.

## 3. Memory for Specialized Agents

While the overall conversational memory is managed centrally, individual specialized agents may also maintain their own short-term memory or context relevant to their specific tasks.

*   **Search Agent:** May remember previous search queries and results to refine subsequent searches or avoid redundant retrievals.
*   **SQL Agent:** Might retain knowledge of recently queried tables or common query patterns to optimize future SQL generation.
*   **Vision Agent:** Could remember previously analyzed images or visual elements to avoid re-processing and build upon prior visual understanding.

## 4. Project Completion Tracking (Progress Ledger)

In addition to conversational memory and per-request agent state, OmniBrain maintains a **Progress Ledger**: a persistent, append-only record of build/implementation status across the project's lifecycle. This is distinct from the runtime state described in Sections 1–3, which tracks the state of a single query's execution. The Progress Ledger instead tracks the state of the *project itself* — which modules exist, which are functional, which are being tested, and what remains — so that any agent (or human contributor) picking up the work in a new session can immediately understand where things stand without re-reading code or prior chat history.

This is maintained in two synchronized forms:

### 4.1 Human-Readable Log (`PROGRESS_LOG.md`)

A markdown file at the project root, updated chronologically (newest entry on top), giving a narrative audit trail. Example:

```markdown
## Progress Log

### 2026-07-16
- [DONE] Vector DB (Qdrant) instance provisioned and text-chunk schema defined.
- [DONE] Embedding pipeline (text-embedding-3-small) wired into ingestion.
- [IN PROGRESS] CLIP-based image embedding — basic pipeline works, metadata tagging pending.
- [BLOCKED] Table extraction (Camelot) — failing on multi-column financial tables, needs fallback logic.

### 2026-07-10
- [DONE] FastAPI gateway scaffolded with /upload and /query endpoints.
- [DONE] Streamlit UI shell connected to gateway.
- [NOT STARTED] SQL Agent — schema introspection logic not yet designed.
```

### 4.2 Machine-Queryable Table (`project_status`)

A relational table (same Postgres instance used for state persistence, per Section 2) that agents query programmatically before starting work, so routing/planning decisions account for what's already built. This is the source of truth the markdown log is generated/synced from.

**Module-level table** — one row per major component, always reflecting current status:

| Column | Description |
|---|---|
| `module_id` | e.g. `search_agent`, `sql_agent`, `vision_agent`, `ingestion_pipeline`, `supervisor`, `guardrails` |
| `status` | `not_started` \| `in_progress` \| `completed` \| `blocked` |
| `last_updated` | Timestamp of last status change |
| `owner` | Agent or contributor responsible |
| `summary` | One-line current state |

**Task-level table** — fine-grained log underneath each module, one row per discrete task/feature:

| Column | Description |
|---|---|
| `task_id` | Unique ID |
| `module_id` | FK to the module-level table |
| `description` | e.g. "Wire CLIP embeddings into ingestion pipeline" |
| `status` | `not_started` \| `in_progress` \| `completed` \| `blocked` |
| `created_at` / `completed_at` | Timestamps |
| `agent` | Which agent/session performed or is performing the task |
| `notes` | Free-text context, blockers, links to relevant files or PRs |
| `depends_on` | Optional FK(s) to other `task_id`s, for sequencing |

### 4.3 Update and Read Protocol

*   **On task completion:** the responsible agent (or developer) writes a new row to the task-level table, updates the parent module's `status`/`summary` if it changed, and appends a corresponding line to `PROGRESS_LOG.md`.
*   **On session start:** any agent (Supervisor, Search, SQL, Vision, or a new development/coding agent) first queries the module-level table (and recent task-level rows) to establish current project state before planning further work — preventing duplicated effort or contradictory assumptions about what already exists.
*   **Granularity rule of thumb:** module-level rows answer "is X built?"; task-level rows answer "what exactly was done, when, by whom, and what's blocking it?" Both are kept in sync so a quick glance (module table) and a detailed audit (task table + markdown log) are both possible.

By meticulously managing conversational memory, per-query agent state, and project-level completion tracking, OmniBrain ensures a robust, transparent, and context-aware reasoning process — both for answering user queries and for coordinating its own ongoing development.
