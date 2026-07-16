# OmniBrain Architecture

This document outlines the high-level architecture of the OmniBrain Agentic Multi-Modal RAG Orchestrator. The system is designed to be modular, scalable, and capable of handling complex reasoning tasks across diverse data modalities.

## System Overview

OmniBrain follows a multi-agent architecture orchestrated by LangGraph. The system consists of several key components:

1.  **User Interface (Streamlit):** The frontend where users interact with the system, submit queries, and view the generated responses, agent thought processes, and citations.
2.  **API Gateway (FastAPI):** The backend that handles requests from the UI, manages document uploads, and initiates the agentic workflow.
3.  **Agentic Orchestrator (LangGraph):** The core component that manages the state machine, routes tasks to specialized agents, and synthesizes the final response.
4.  **Specialized Agents:**
    *   **Search Agent:** Retrieves semantic text from the vector database.
    *   **SQL Agent:** Queries structured data from relational databases.
    *   **Vision Agent:** Extracts and reasons over visual data (charts, graphs) using VLMs.
5.  **Data Storage:**
    *   **Vector Database (FAISS):** Stores text chunks and image embeddings for semantic search (Local in-memory DB selected per minimal-dependency philosophy).
    *   **Relational Database (SQLite):** Stores structured historical data (e.g., stock prices). Used as a local file DB to avoid PostgreSQL docker overhead.
6.  **Evaluation & Guardrails:**
    *   **NeMo Guardrails:** Enforces content policies and prevents hallucinations.
    *   **Langfuse:** Tracks token usage, latency, and execution traces for observability.

## Workflow

1.  **Document Ingestion:**
    *   Users upload documents (e.g., PDFs) via the UI.
    *   The API Gateway receives the document and initiates the ingestion pipeline.
    *   The pipeline parses the document, extracts text, tables, and images.
    *   Text is chunked and embedded using an embedding model (e.g., OpenAI's `text-embedding-3-small`).
    *   Images are embedded using a multimodal model (e.g., CLIP).
    *   Embeddings and metadata are stored in the Vector Database.

2.  **Query Processing:**
    *   The user submits a query via the UI.
    *   The API Gateway forwards the query to the Agentic Orchestrator.
    *   The **Supervisor Agent** evaluates the query and determines the necessary steps and specialized agents required to answer it.

3.  **Agent Execution:**
    *   The Supervisor Agent routes tasks to the appropriate specialized agents.
    *   **Search Agent:** Queries the Vector Database for relevant text chunks.
    *   **SQL Agent:** Translates natural language queries into SQL and executes them against the Relational Database.
    *   **Vision Agent:** Retrieves relevant images from the Vector Database and uses a VLM (e.g., GPT-4o) to extract data and reason over them.

4.  **Synthesis and Guardrails:**
    *   The specialized agents return their findings to the Supervisor Agent.
    *   The Supervisor Agent synthesizes the findings into a coherent response.
    *   The response is passed through **NeMo Guardrails** to ensure it is grounded in the retrieved context and adheres to safety policies.

5.  **Response Delivery:**
    *   The final, verified response, along with citations and agent thought processes, is sent back to the UI via the API Gateway.
    *   Execution traces and metrics are logged to **Langfuse** for observability.

## Architecture Diagram

*(A visual representation of the architecture will be added here)*

## Key Technologies

*   **Orchestration:** LangGraph
*   **LLMs/VLMs:** OpenAI GPT-4o, LLaVA (optional for local deployment)
*   **Embeddings:** OpenAI `text-embedding-3-small`, CLIP
*   **Vector Database:** FAISS (Local)
*   **Relational Database:** SQLite (Local)
*   **Guardrails:** NeMo Guardrails
*   **Observability:** Langfuse
*   **Backend:** FastAPI
*   **Frontend:** Streamlit
