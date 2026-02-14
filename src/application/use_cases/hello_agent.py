"""Use case: run Hello Agent flow and return response."""

from src.application.flows.hello_agent import create_hello_agent_graph
from src.application.interfaces.llm_gateway import LLMGateway


class HelloAgentUseCase:
    """Run the Hello Agent LangGraph with given input."""

    def __init__(self, llm_gateway: LLMGateway) -> None:
        self._llm_gateway = llm_gateway
        self._graph = create_hello_agent_graph(llm_gateway)

    def run(self, user_input: str) -> str:
        """Execute the agent and return the greeting response."""
        initial_state: dict = {
            "messages": [],
            "current_input": user_input,
            "response": "",
        }
        result = self._graph.invoke(initial_state)
        return result.get("response", "")
