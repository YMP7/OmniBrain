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

By meticulously managing both conversational and agentic state, OmniBrain ensures a robust, transparent, and context-aware reasoning process, leading to more accurate and helpful responses.
