import sqlite3
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "omnibrain.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS project_status_module (
        module_id     VARCHAR(50) PRIMARY KEY,
        status        VARCHAR(20) NOT NULL CHECK (status IN ('not_started','in_progress','completed','blocked')),
        last_updated  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        owner         VARCHAR(100),
        summary       TEXT
    );

    CREATE TABLE IF NOT EXISTS project_status_task (
        task_id       INTEGER PRIMARY KEY AUTOINCREMENT,
        module_id     VARCHAR(50) REFERENCES project_status_module(module_id),
        description   TEXT NOT NULL,
        status        VARCHAR(20) NOT NULL CHECK (status IN ('not_started','in_progress','completed','blocked')),
        created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        completed_at  TIMESTAMP,
        agent         VARCHAR(100),
        notes         TEXT,
        depends_on    INTEGER REFERENCES project_status_task(task_id)
    );

    INSERT OR IGNORE INTO project_status_module (module_id, status, owner, summary) VALUES
    ('architecture_design',   'completed',   'planning',   'Full system architecture, workflow, and tech stack documented.'),
    ('ingestion_pipeline',    'not_started', 'unassigned', 'PDF parsing, OCR, table extraction, chunking, embedding — not yet built.'),
    ('vector_db',             'not_started', 'unassigned', 'Qdrant/FAISS not yet provisioned.'),
    ('relational_db',         'not_started', 'unassigned', 'PostgreSQL/MySQL not yet provisioned for structured stock/financial data.'),
    ('supervisor_agent',      'not_started', 'unassigned', 'LangGraph state machine and routing logic not yet implemented.'),
    ('search_agent',          'not_started', 'unassigned', 'Semantic retrieval logic not yet implemented.'),
    ('sql_agent',             'not_started', 'unassigned', 'Text-to-SQL generation and execution not yet implemented.'),
    ('vision_agent',          'not_started', 'unassigned', 'VLM integration for chart/image reasoning not yet implemented.'),
    ('memory_state_mgmt',     'completed',   'planning',   'Conversational memory, LangGraph state, and Progress Ledger design finalized.'),
    ('guardrails_eval',       'not_started', 'unassigned', 'NeMo Guardrails and Langfuse not yet integrated.'),
    ('api_gateway',           'not_started', 'unassigned', 'FastAPI backend not yet scaffolded.'),
    ('frontend_ui',           'not_started', 'unassigned', 'Streamlit UI not yet scaffolded.');

    INSERT OR IGNORE INTO project_status_task (module_id, description, status, agent, notes) VALUES
    ('architecture_design', 'Draft and finalize system overview, workflow, and key technologies', 'completed', 'planning-session', 'Documented in OmniBrain_Architecture.md'),
    ('memory_state_mgmt',   'Define conversational memory, agent state, and state persistence approach', 'completed', 'planning-session', 'Documented in OmniBrain_Memory_and_State_Management.md, Sections 1-3'),
    ('memory_state_mgmt',   'Design Progress Ledger (module + task-level tracking) for project completion status', 'completed', 'planning-session', 'Documented in OmniBrain_Memory_and_State_Management.md, Section 4'),
    ('supervisor_agent',    'Design LangGraph node/edge structure for query routing', 'completed', 'planning-session', 'Design documented in Supervisor_Agent.md; not yet implemented in code'),
    ('search_agent',        'Design semantic retrieval workflow', 'completed', 'planning-session', 'Design documented in Search_Agent.md; not yet implemented in code'),
    ('sql_agent',           'Design text-to-SQL workflow', 'completed', 'planning-session', 'Design documented in SQL_Agent.md; not yet implemented in code'),
    ('vision_agent',        'Design VLM-based chart/image reasoning workflow', 'completed', 'planning-session', 'Design documented in Vision_Agent.md; not yet implemented in code');
    ''')
    
    conn.commit()
    conn.close()
    print("SQLite database initialized successfully.")

if __name__ == '__main__':
    init_db()
