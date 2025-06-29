from typing import Annotated, Literal

from langchain.schema import Document
from langgraph.graph.message import BaseMessage, add_messages
from pydantic import BaseModel


def add_reasoning(existing: str, new: str) -> str:
    """
    Reducer function to concatenate reasoning strings.

    Args:
        existing: Current reasoning string
        new: New reasoning to add

    Returns:
        Concatenated reasoning string
    """
    return existing + new


class SessionState(BaseModel):
    """State of the session."""

    # full message history (user / assistant)
    messages: Annotated[list[BaseMessage], add_messages]

    # high-level branch chosen by intent classifier
    intent: Literal["chat", "research"] | None = None

    # retrieved docs & their sources (for research branch only)
    docs: list[Document] = []
    sources: list[str] = []

    # internal reasoning (for research branch only) - accumulates text
    reasoning: str = ""

    # final answer (for research branch only)
    answer: str | None = None
