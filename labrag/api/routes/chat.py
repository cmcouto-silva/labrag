"""Chat API routes."""

from fastapi import APIRouter
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from loguru import logger
from pydantic import BaseModel

from labrag.agents.graph import create_graph
from labrag.agents.state import SessionState
from labrag.ingestion.loaders.vector_store import VectorStore

router = APIRouter()

# Initialize the vector store, memory checkpointer, and LangGraph graph once on startup
vector_store = VectorStore()
# In-memory checkpoint so each session/thread keeps its own state automatically
memory = InMemorySaver()

graph = create_graph(vector_store).compile(checkpointer=memory)


class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    response: str
    session_id: str


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Chat endpoint backed by LangGraph agent."""
    # Prepare LangGraph state with the new human message
    logger.debug(f"Session ID: {request.session_id}")
    state = SessionState(messages=[HumanMessage(content=request.message)])

    # Each unique session_id becomes the LangGraph thread_id
    thread_config = {"configurable": {"thread_id": request.session_id}}

    # Run graph asynchronously and obtain updated state
    response = await graph.ainvoke(state, config=thread_config)

    # The assistant reply is the last message in the conversation history
    last_reply = response.get("messages", [])[-1].content

    return ChatResponse(response=last_reply, session_id=request.session_id)
