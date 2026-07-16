# Supervisor Agent

The Supervisor Agent is the central orchestrator of the OmniBrain system, implemented using LangGraph. It acts as the "brain" of the operation, responsible for understanding the user's query, breaking it down into manageable sub-tasks, and routing these tasks to the appropriate specialized agents.

## Role and Responsibilities

The primary role of the Supervisor Agent is to manage the overall workflow and ensure that the user's query is answered accurately and comprehensively. Its key responsibilities include:

1.  **Query Analysis:** The agent analyzes the incoming user query to determine its intent and the types of information required to formulate a response. It identifies whether the query requires semantic text search, structured data querying, visual data interpretation, or a combination of these.
2.  **Task Routing:** Based on the query analysis, the Supervisor Agent routes specific sub-tasks to the relevant specialized agents (Search Agent, SQL Agent, Vision Agent). It determines the optimal sequence of execution, which may involve parallel processing or sequential dependencies.
3.  **State Management:** The agent maintains the state of the conversation and the progress of the various sub-tasks. It keeps track of the information retrieved by the specialized agents and uses this context to guide subsequent actions.
4.  **Synthesis and Formatting:** Once all necessary information has been gathered, the Supervisor Agent synthesizes the findings into a coherent and well-structured response. It ensures that the final output directly addresses the user's query and includes appropriate citations to the source documents.
5.  **Error Handling and Self-Correction:** The agent monitors the outputs of the specialized agents. If an agent fails to retrieve relevant information or encounters an error, the Supervisor Agent can initiate a self-correction loop, prompting the agent to refine its search strategy or try an alternative approach.

## Implementation Details

The Supervisor Agent is implemented as a state machine using LangGraph. The state object contains the user's query, the conversation history, the intermediate findings from the specialized agents, and the current status of the workflow.

The agent utilizes a Large Language Model (LLM), such as GPT-4o, to perform its reasoning and decision-making tasks. The LLM is provided with a system prompt that defines its role, available tools (the specialized agents), and instructions on how to route tasks and synthesize information.

### LangGraph Nodes and Edges

The LangGraph implementation consists of several nodes and edges:

*   **Nodes:** Represent the different states or actions in the workflow, such as "Analyze Query," "Route to Search Agent," "Route to SQL Agent," "Route to Vision Agent," and "Synthesize Response."
*   **Edges:** Define the transitions between nodes based on the outcomes of the actions. For example, an edge might connect the "Analyze Query" node to the "Route to Search Agent" node if the query requires semantic text retrieval. Conditional edges are used to implement decision logic, such as determining which agent to call next based on the current state.

## Example Workflow

1.  **User Query:** "What was the revenue growth in Q3 2023, and how does it compare to the projected growth shown in the Q2 presentation chart?"
2.  **Supervisor Analysis:** The Supervisor Agent identifies two sub-tasks:
    *   Retrieve revenue growth data for Q3 2023 (requires SQL Agent or Search Agent).
    *   Analyze the projected growth chart from the Q2 presentation (requires Vision Agent).
3.  **Task Routing:** The Supervisor Agent routes the first task to the SQL Agent (if the data is in a structured database) or the Search Agent (if it's in a text document). It routes the second task to the Vision Agent.
4.  **Information Gathering:** The specialized agents execute their tasks and return the results to the Supervisor Agent.
5.  **Synthesis:** The Supervisor Agent combines the retrieved revenue data and the insights from the chart analysis to formulate a comprehensive response, comparing the actual growth with the projected growth.
6.  **Final Output:** The synthesized response, along with citations to the specific database records and the Q2 presentation chart, is presented to the user.
