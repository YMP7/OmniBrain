# SQL Agent

The SQL Agent in OmniBrain is designed to interact with structured databases, translating natural language queries into SQL commands and executing them to retrieve specific data. This agent is crucial for accessing historical data, financial records, or any information stored in relational databases.

## Role and Responsibilities

The primary role of the SQL Agent is to enable the OmniBrain system to query structured data sources. Its key responsibilities include:

1.  **Natural Language to SQL Conversion:** The agent receives a natural language question or instruction from the Supervisor Agent and converts it into an executable SQL query. This often involves understanding the schema of the target database.
2.  **Database Interaction:** It connects to and executes the generated SQL queries against a specified relational database (e.g., PostgreSQL, MySQL).
3.  **Data Retrieval:** The agent retrieves the results of the SQL query, which typically consist of tabular data.
4.  **Result Formatting:** It formats the retrieved data into a structured, readable format (e.g., JSON, Markdown table) suitable for the Supervisor Agent to integrate into the final response.
5.  **Error Handling:** The agent is responsible for handling potential SQL errors, such as invalid queries or connection issues, and reporting them back to the Supervisor Agent.

## Implementation Details

The SQL Agent typically utilizes a Text-to-SQL model or a combination of an LLM with database schema knowledge to generate accurate SQL queries. Python libraries like SQLAlchemy or `psycopg2` (for PostgreSQL) can be used for database connectivity and execution.

### Key Components:

*   **Text-to-SQL Model/LLM:** An LLM fine-tuned for Text-to-SQL tasks or a general-purpose LLM provided with the database schema (table names, column names, data types) to generate correct SQL queries.
*   **Database Connector:** A Python library to establish and manage connections to the relational database.
*   **Query Executor:** Logic to safely execute the generated SQL queries and fetch results.
*   **Schema Information:** The agent needs access to the database schema (e.g., `CREATE TABLE` statements or an ORM model) to accurately generate SQL queries.

## Example Workflow

1.  **Supervisor Agent Request:** The Supervisor Agent receives a query like "What was the total revenue for the last quarter of 2023?" and identifies that this information resides in a structured financial database.
2.  **SQL Query Generation:** The SQL Agent, with knowledge of the financial database schema, translates this into a SQL query, e.g., `SELECT SUM(revenue) FROM financial_data WHERE quarter = 'Q4' AND year = 2023;`
3.  **Database Execution:** The agent executes this query against the financial database.
4.  **Data Retrieval:** The database returns the sum of revenue for Q4 2023.
5.  **Return to Supervisor:** The SQL Agent formats this numerical result and returns it to the Supervisor Agent for integration into the final answer.
