from functools import partial

from langgraph.graph import END, START, StateGraph

from labrag.agents.nodes import (
    chat_agent_node,
    intent_classifier_node,
    retriever_node,
    synthesizer_node,
)
from labrag.agents.state import SessionState
from labrag.ingestion.loaders.vector_store import VectorStore


def create_graph(vector_store: VectorStore) -> StateGraph:
    workflow = StateGraph(SessionState)

    workflow.add_node("intent_classifier", intent_classifier_node)
    workflow.add_node("chat_agent", chat_agent_node)
    workflow.add_node("retriever", partial(retriever_node, vector_store=vector_store))
    workflow.add_node("synthesizer", synthesizer_node)

    workflow.add_edge(START, "intent_classifier")
    workflow.add_conditional_edges(
        "intent_classifier",
        lambda x: x.intent,
        {"research": "retriever", "chat": "chat_agent"},
    )

    workflow.add_edge("retriever", "synthesizer")
    workflow.add_edge("chat_agent", END)
    workflow.add_edge("synthesizer", END)

    return workflow
