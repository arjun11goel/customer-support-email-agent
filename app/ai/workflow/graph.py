from langgraph.graph import END, START, StateGraph

from app.ai.workflow.nodes.classify import classify_email
from app.ai.workflow.nodes.escalation import evaluate_escalation
from app.ai.workflow.nodes.generate import generate_response
from app.ai.workflow.nodes.retrieve import retrieve_knowledge
from app.ai.workflow.nodes.validate import validate_response
from app.ai.workflow.state import AgentState


def build_agent_graph():
    """Build the SupportFlow AI LangGraph workflow."""

    graph = StateGraph(AgentState)

    graph.add_node("classify", classify_email)
    graph.add_node("retrieve", retrieve_knowledge)
    graph.add_node("generate", generate_response)
    graph.add_node("validate", validate_response)
    graph.add_node("escalation", evaluate_escalation)

    graph.add_edge(START, "classify")
    graph.add_edge("classify", "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", "validate")
    graph.add_edge("validate", "escalation")
    graph.add_edge("escalation", END)

    return graph.compile()


agent_graph = build_agent_graph()