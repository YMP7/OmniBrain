import os
import sqlite3
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS

import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FAISS_INDEX_PATH = os.path.join(PROJECT_ROOT, "faiss_index")
SQLITE_DB_PATH = os.path.join(PROJECT_ROOT, "omnibrain.db")

# ---------------------------------------------------------
# 1. Search Agent
# ---------------------------------------------------------
def search_agent(query: str, k: int = 3) -> str:
    """
    Retrieves semantic text from the local FAISS index.
    """
    if not os.environ.get("OPENAI_API_KEY"):
        return "ERROR: OPENAI_API_KEY is missing."
        
    if not os.path.exists(FAISS_INDEX_PATH):
        return "ERROR: FAISS index not found. Please run ingestion first."
        
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    
    docs = vectorstore.similarity_search(query, k=k)
    
    if not docs:
        return "No relevant documents found."
        
    results = []
    for doc in docs:
        source = doc.metadata.get("source", "Unknown Source")
        page = doc.metadata.get("page", "Unknown Page")
        results.append(f"[Source: {source}, Page: {page}]\n{doc.page_content}")
        
    return "\n\n---\n\n".join(results)

# ---------------------------------------------------------
# 2. SQL Agent
# ---------------------------------------------------------
def get_schema() -> str:
    """Introspect the SQLite DB to get the schema for the LLM."""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    schema_statements = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()
    return "\n\n".join(schema_statements)

def sql_agent(query: str) -> str:
    """
    Translates a natural language query into SQL, executes it against SQLite, 
    and returns the tabular result.
    """
    if not os.environ.get("OPENAI_API_KEY"):
        return "ERROR: OPENAI_API_KEY is missing."

    schema = get_schema()
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    # Very minimal text-to-SQL prompt
    prompt = f"""
    You are a SQL agent. Generate ONLY a valid SQLite SELECT query based on the following schema and user question.
    Do not wrap in markdown blocks, just return the raw SQL string.
    
    SCHEMA:
    {schema}
    
    QUESTION: {query}
    """
    
    sql_query = llm.invoke(prompt).content.strip()
    
    # Remove markdown code blocks if the LLM included them despite instructions
    if sql_query.startswith("```sql"):
        sql_query = sql_query[6:].strip()
    if sql_query.endswith("```"):
        sql_query = sql_query[:-3].strip()
        
    # Enforce read-only execution
    if not sql_query.upper().startswith("SELECT"):
        return f"ERROR: The SQL Agent is restricted to read-only SELECT queries. Generated query rejected: {sql_query}"
    
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        conn.close()
        
        # Format as minimal markdown table
        header = " | ".join(columns)
        separator = " | ".join(["---"] * len(columns))
        rows = [" | ".join(map(str, row)) for row in results]
        return "\n".join([header, separator] + rows)
    except Exception as e:
        return f"SQL Error executing query '{sql_query}': {e}"

# ---------------------------------------------------------
# 3. Vision Agent
# ---------------------------------------------------------
def vision_agent(query: str, image_path: str) -> str:
    """
    Uses OpenAI's vision model to reason over a specific extracted image.
    """
    import base64
    if not os.environ.get("OPENAI_API_KEY"):
        return "ERROR: OPENAI_API_KEY is missing."
        
    if not os.path.exists(image_path):
        return f"ERROR: Image not found at {image_path}"
        
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": query},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
            ]
        }
    ]
    
    return llm.invoke(messages).content
