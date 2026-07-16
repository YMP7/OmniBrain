from typing import TypedDict, Sequence, Annotated
import operator
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
import os
import json

import os
from .agents import search_agent, sql_agent, vision_agent

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# ---------------------------------------------------------
# State Definition
# ---------------------------------------------------------
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    intermediate_findings: Annotated[str, operator.add]
    next_agent: str
    step_count: int
    image_path: str # Optional, if vision is needed

# ---------------------------------------------------------
# Supervisor Node
# ---------------------------------------------------------
def supervisor_node(state: AgentState):
    """
    Analyzes the query and routes to the appropriate specialized agent, 
    or synthesizes the final answer if findings are sufficient.
    """
    messages = state.get("messages", [])
    findings = state.get("intermediate_findings", "")
    step_count = state.get("step_count", 0) + 1
    
    if step_count >= 6:
        # Loop guard: force synthesize
        return {"next_agent": "FINISH", "step_count": step_count}
        
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    system_prompt = f"""
    You are the OmniBrain Supervisor Agent. Your job is to route the user's query to one of three specialized agents, or synthesize a final answer if you have enough information.
    
    Current Findings: {findings}
    
    Available Routing Options:
    - 'search': For semantic text retrieval from documents.
    - 'sql': For querying structured historical/financial data.
    - 'vision': For analyzing charts or images (assume the user has provided an image context if they ask about a visual).
    - 'FINISH': If the user's query is answered by the Current Findings or is a simple conversational turn.
    
    Respond with ONLY a JSON object containing two keys: "next_action" (one of the routing options) and "reasoning" (brief explanation).
    """
    
    response = llm.invoke([SystemMessage(content=system_prompt)] + list(messages))
    
    response_content = response.content.strip()
    if response_content.startswith("```json"):
        response_content = response_content[7:].strip()
    if response_content.endswith("```"):
        response_content = response_content[:-3].strip()
        
    try:
        decision = json.loads(response_content)
        next_agent = decision.get("next_action", "FINISH")
    except json.JSONDecodeError:
        next_agent = "FINISH"
        
    return {"next_agent": next_agent, "step_count": step_count}

# ---------------------------------------------------------
# Specialized Agent Nodes
# ---------------------------------------------------------
def search_node(state: AgentState):
    query = state["messages"][-1].content
    result = search_agent(query)
    return {"intermediate_findings": f"\n\n[Search Agent]\n{result}", "next_agent": "supervisor"}

def sql_node(state: AgentState):
    query = state["messages"][-1].content
    result = sql_agent(query)
    return {"intermediate_findings": f"\n\n[SQL Agent]\n{result}", "next_agent": "supervisor"}

def vision_node(state: AgentState):
    query = state["messages"][-1].content
    findings = state.get("intermediate_findings", "")
    
    import re
    # Dynamically build image path from the last search citation (e.g., [Source: doc.pdf, Page: 4])
    image_path = state.get("image_path", os.path.join(PROJECT_ROOT, "extracted_images", "sample_page1.png")) 
    matches = re.findall(r"\[Source: (.*?), Page: (\d+)\]", findings)
    if matches:
        last_source, last_page = matches[-1]
        image_path = os.path.join(PROJECT_ROOT, "extracted_images", f"{last_source}_page{last_page}.png")
        
    result = vision_agent(query, image_path)
    return {"intermediate_findings": f"\n\n[Vision Agent]\n{result}", "next_agent": "supervisor"}

def synthesize_node(state: AgentState):
    """Generates the final response based on accumulated findings with strict grounding."""
    messages = state["messages"]
    findings = state.get("intermediate_findings", "")
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    system_prompt = f"""
    You are the OmniBrain Synthesizer. Answer the user's question based STRICTLY on the provided findings.
    
    CRITICAL RULE: For EVERY factual claim you make, you MUST append a citation in the format [Source: X, Page: Y] using the metadata provided in the findings.
    If the findings do not contain enough information to answer the question, or if you cannot find a source and page to cite for a factual claim, you MUST reject the request by replying with EXACTLY: 
    "REJECTED: I cannot answer this because there is no supporting citation in the retrieved context."
    
    Do not make up information. Do not omit citations.
    
    Findings:
    {findings}
    """
    
    response = llm.invoke([SystemMessage(content=system_prompt)] + list(messages))
    
    # Minimal guardrail check: if it's not a rejection and doesn't contain a citation format, flag it
    content = response.content
    if "REJECTED" not in content and "[Source:" not in content and findings.strip():
        # A soft-retry/flag mechanism honoring Ponytail simplicity
        content = "REJECTED (Guardrail Flag): The synthesized response contained factual claims but failed to provide proper citations. Please try rephrasing your query."
        response = AIMessage(content=content)
        
    return {"messages": [response]}

# ---------------------------------------------------------
# Router Edge
# ---------------------------------------------------------
def router(state: AgentState):
    next_agent = state.get("next_agent")
    if next_agent == "search":
        return "search"
    elif next_agent == "sql":
        return "sql"
    elif next_agent == "vision":
        return "vision"
    else:
        return "synthesize"

# ---------------------------------------------------------
# Graph Construction
# ---------------------------------------------------------
workflow = StateGraph(AgentState)

workflow.add_node("supervisor", supervisor_node)
workflow.add_node("search", search_node)
workflow.add_node("sql", sql_node)
workflow.add_node("vision", vision_node)
workflow.add_node("synthesize", synthesize_node)

workflow.set_entry_point("supervisor")

workflow.add_conditional_edges("supervisor", router, {
    "search": "search",
    "sql": "sql",
    "vision": "vision",
    "synthesize": "synthesize"
})

workflow.add_edge("search", "supervisor")
workflow.add_edge("sql", "supervisor")
workflow.add_edge("vision", "supervisor")
workflow.add_edge("synthesize", END)

# Compile the graph
omni_brain_app = workflow.compile()
