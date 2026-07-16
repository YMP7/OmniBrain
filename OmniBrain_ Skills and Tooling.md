# OmniBrain: Skills and Tooling

OmniBrain's effectiveness stems from its modular design, where specialized agents leverage a suite of distinct skills and external tools to perform their tasks. These skills encapsulate specific functionalities, allowing agents to interact with various data sources, process different modalities, and ensure the quality and safety of the generated responses.

## 1. Data Parsing Skills

These skills are fundamental for ingesting and preparing raw, unstructured, and semi-structured data from diverse document formats into a usable format for the agents.

### Tools & Technologies:

*   **PDF Parsers (e.g., `PyPDF2`, `pdfminer.six`):** For extracting text content from PDF documents.
*   **Optical Character Recognition (OCR) (e.g., `Tesseract`, cloud-based OCR APIs):** To convert images of text (e.g., scanned documents, text within images) into machine-readable text.
*   **Table Extraction Libraries (e.g., `Camelot`, `Tabula-py`):** For identifying and extracting tabular data from PDFs and images, converting them into structured formats like DataFrames.
*   **Image Processing Libraries (e.g., `Pillow`, `OpenCV`):** For pre-processing images (e.g., cropping, resizing, enhancing) before feeding them to Vision-Language Models.

## 2. Retrieval Skills

Retrieval skills enable agents to efficiently search and retrieve relevant information from vast datasets, supporting both semantic and exact-match queries across different data types.

### Tools & Technologies:

*   **Embedding Models (e.g., OpenAI `text-embedding-3-small`, CLIP):** To convert text and images into high-dimensional vector embeddings, crucial for semantic similarity search.
*   **Vector Databases (FAISS):** For storing and indexing vector embeddings, allowing for fast similarity searches. FAISS is used for in-memory, high-performance similarity search, avoiding the overhead of a dedicated Qdrant server during local development.
*   **Relational Database Connectors (e.g., `sqlite3`, SQLAlchemy):** For connecting to and querying traditional SQL databases (SQLite) to retrieve structured historical data.

## 3. Reasoning and Synthesis Skills

These skills empower agents to process retrieved information, perform logical deductions, and combine disparate pieces of data into coherent and insightful responses.

### Tools & Technologies:

*   **Large Language Models (LLMs) (e.g., GPT-4o):** Used by the Supervisor Agent for query analysis, task routing, and synthesizing final responses. Also used by the SQL Agent for Text-to-SQL conversion and by the Search Agent for refining search queries.
*   **Vision-Language Models (VLMs) (e.g., GPT-4o with vision, LLaVA):** Utilized by the Vision Agent to interpret visual content, extract data from charts, and answer questions about images.
*   **LangGraph:** The primary framework for defining and orchestrating the state machine of the Supervisor Agent, enabling complex multi-step reasoning and dynamic task routing.
*   **Text-to-SQL Engines (e.g., custom LLM-based solutions, specialized APIs):** For converting natural language questions into executable SQL queries, used by the SQL Agent.

## 4. Guardrail Skills

Guardrail skills are critical for ensuring the safety, accuracy, and ethical compliance of OmniBrain's outputs, preventing hallucinations and adherence to predefined policies.

### Tools & Technologies:

*   **NeMo Guardrails:** An open-source toolkit for building programmable guardrails for LLM-based systems. It enforces content policies, prevents off-topic responses, and ensures responses are grounded in retrieved information.
*   **Langfuse:** An observability platform for LLM applications. It tracks and visualizes LLM calls, traces, and evaluations, providing insights into token usage, latency, and model behavior, which is essential for monitoring and improving guardrail effectiveness.
*   **Self-Correction Logic:** Custom-implemented logic within agents (e.g., the Self-RAG mechanism) that allows them to detect irrelevant retrievals or incorrect reasoning and autonomously attempt to correct their approach before generating a final response.
