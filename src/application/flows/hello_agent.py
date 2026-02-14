"""Hello Agent: minimal LangGraph flow for greeting the user."""

from typing import Annotated, TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from src.application.interfaces.llm_gateway import LLMGateway


class HelloAgentState(TypedDict):
    """State schema for Hello Agent graph (LangGraph compatible)."""
    messages: Annotated[list, add_messages]
    current_input: str
    response: str


def create_hello_agent_graph(llm_gateway: LLMGateway):
    """
    Build and compile the Hello Agent LangGraph.
    Uses LLMGateway for LLM calls (inject from infrastructure).
    """
    def process_node(state: HelloAgentState) -> dict:
        user_input = state.get("current_input", "").strip() or "World"
        reply = llm_gateway.invoke(
            f"Generate a short friendly greeting for the name: {user_input}. Reply with only the greeting, no quotes."
        )
        return {"response": reply.strip(), "messages": [{"role": "assistant", "content": reply}]}

    graph = StateGraph(HelloAgentState)
    graph.add_node("process", process_node)
    graph.add_edge(START, "process")
    graph.add_edge("process", END)

    return graph.compile()
