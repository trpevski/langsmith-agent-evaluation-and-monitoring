"""Agent implementation with LangSmith tracing."""

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langsmith import get_tracer
from typing import TypedDict, Annotated, List
from .config import OPENAI_MODEL, AGENT_TEMPERATURE, MAX_AGENT_STEPS
from .tools import (
    search_documentation,
    fetch_user_data,
    create_summary,
    get_usage_metrics,
    list_available_features,
)


class AgentState(TypedDict):
    """State schema for the agent graph."""

    messages: List[dict]
    tool_results: List[dict]
    cost: float
    step_count: int
    user_id: str


def create_agent():
    """
    Create and compile the agent graph.

    Returns:
        Compiled agent graph
    """
    # Initialize LLM with tracing enabled
    llm = ChatOpenAI(
        model=OPENAI_MODEL, temperature=AGENT_TEMPERATURE, temperature_override=True
    )

    tools = [
        search_documentation,
        fetch_user_data,
        create_summary,
        get_usage_metrics,
        list_available_features,
    ]

    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)

    def agent_node(state: AgentState):
        """
        Main agent reasoning step.

        Args:
            state: Current agent state

        Returns:
            Updated state with new messages
        """
        tracer = get_tracer()

        # Each step is traced automatically
        with tracer.trace("agent_reasoning") as run:
            # Prepare messages
            messages = state.get("messages", [])

            # Get response from LLM
            response = llm_with_tools.invoke(messages)

            # Track metadata
            run.add_tags([f"step_count:{state['step_count']}", f"user:{state.get('user_id', 'unknown')}"])

            return {
                "messages": messages + [response],
                "step_count": state["step_count"] + 1,
                "cost": state.get("cost", 0) + 0.002,  # Track cumulative cost
                "tool_results": [],
                "user_id": state.get("user_id", "unknown"),
            }

    def should_continue(state: AgentState):
        """
        Decide if we need more steps or we're done.

        Args:
            state: Current agent state

        Returns:
            Next node name or END
        """
        if state["step_count"] >= MAX_AGENT_STEPS:
            return END

        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    # Build the graph
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))

    workflow.add_edge("tools", "agent")
    workflow.add_conditional_edges(
        "agent", should_continue, {"tools": "tools", END: END}
    )
    workflow.set_entry_point("agent")

    return workflow.compile()


def run_agent(agent, query: str, user_id: str = "default") -> dict:
    """
    Run the agent with a given query.

    Args:
        agent: Compiled agent graph
        query: User query/input
        user_id: User identifier for tracking

    Returns:
        Agent result dictionary
    """
    from langchain.schema import HumanMessage

    result = agent.invoke(
        {
            "messages": [HumanMessage(content=query)],
            "tool_results": [],
            "cost": 0,
            "step_count": 0,
            "user_id": user_id,
        }
    )

    return {
        "query": query,
        "response": result["messages"][-1] if result["messages"] else None,
        "steps": result["step_count"],
        "cost": result["cost"],
        "user_id": user_id,
    }
