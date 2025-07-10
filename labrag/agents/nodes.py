import json
from typing import Any

from langchain.chat_models import init_chat_model
from langchain.schema import AIMessage
from loguru import logger

from labrag.agents.state import SessionState
from labrag.agents.utils import (
    format_document_context,
    format_sources_with_pages,
    get_chat_history,
)
from labrag.config import load_prompt_templates
from labrag.ingestion.loaders.vector_store import VectorStore


async def intent_classifier_node(state: SessionState) -> dict[str, Any]:
    """Classify user intent: research or casual chat."""
    logger.info("Intent Classifier Node")
    llm = init_chat_model("gpt-4.1-mini", model_provider="openai", temperature=0)

    prompt = load_prompt_templates()["route_intent_system_prompt"].format(
        conversation_context=get_chat_history(state.messages),
        latest_message=state.messages[-1].content if state.messages else "",
    )

    logger.debug(f"Intent classifier prompt: {prompt}")

    response = await llm.ainvoke(prompt)
    try:
        result = json.loads(response.content)
        intent = result.get("intent", "chat")
    except Exception as e:
        logger.error(f"Error parsing intent classifier response: {e}")
        intent = "chat"  # default to chat if parsing fails

    return {
        "intent": intent,
        "reasoning": f"**Step 1. Intent classification** — {intent}\n\n",
    }


async def chat_agent_node(state: SessionState) -> dict[str, Any]:
    """Handle casual conversation with session memory."""
    logger.info("Chat Agent Node")
    latest_message = state.messages[-1].content if state.messages else ""

    # Get conversation history for context
    conversation_context = get_chat_history(state.messages)

    llm = init_chat_model("gpt-4.1", model_provider="openai", temperature=0.5)

    prompt = load_prompt_templates()["chat_agent_system_prompt"].format(
        conversation_context=conversation_context, latest_message=latest_message
    )

    logger.debug(f"Chat Agent prompt: {prompt}")

    response = await llm.ainvoke(prompt)
    ai_message = AIMessage(content=response.content)

    return {"messages": [ai_message]}


async def retriever_node(
    state: SessionState, vector_store: VectorStore
) -> dict[str, Any]:
    """Document Retrieval"""
    logger.info("Document Retrieval Node")
    latest_message = state.messages[-1].content if state.messages else ""

    logger.debug(f"Document retrieval query: {latest_message[:50]}...")

    docs = await vector_store.asearch(latest_message, k=30)
    sources = format_sources_with_pages(docs)

    logger.debug(
        f"Document retrieval result: Found {len(docs)} "
        f"documents from {len(sources)} sources"
    )

    reasoning = (
        state.reasoning + f"**Step 2. Document Retrieval** — Retrieved {len(docs)} "
        f"documents chunks from {len(sources)} sources\n"
    )

    return {
        "docs": docs,
        "sources": sources,
        "reasoning": reasoning,
    }


async def synthesizer_node(state: SessionState) -> dict[str, Any]:
    """Response Synthesis"""
    logger.info("Response Synthesis Node")
    latest_message = state.messages[-1].content if state.messages else ""

    # Get context from retrieved documents
    context = format_document_context(state.docs)

    # Get conversation history
    conversation_context = get_chat_history(state.messages)

    llm = init_chat_model(
        "gpt-4o", model_provider="openai", temperature=0.7
    ).with_structured_output(method="json_mode")

    prompt_template = load_prompt_templates()["research_synthesis_prompt"]
    prompt = prompt_template.format(
        query=latest_message,
        context=context,
        conversation_context=conversation_context,
        sources=state.sources,
    )

    response = await llm.ainvoke(prompt)
    logger.debug(f"Synthesis response: {response}")

    final_answer = response.get("main_answer", "")
    references = response.get("references", [])
    document_analysis = response.get("document_analysis", [])

    # Format the final answer
    formatted_answer = f"## Final Answer\n{final_answer}\n\n"

    if references:
        formatted_answer += "## References\n"
        for ref in references:
            formatted_answer += f"- {ref}\n"
        formatted_answer += "\n"

    state.reasoning += (
        f"\n**Step 3. Response Synthesis:** Synthesized response based on "
        f"{len(document_analysis)} document chunks with proper citations.\n\n"
    )

    if document_analysis:
        formatted_answer += "## Reasoning\n\n" + state.reasoning
        for analysis in document_analysis:
            source = analysis.get("source", "N/A")
            page = analysis.get("page", "N/A")
            reasoning = analysis.get("reasoning", "No reasoning provided.")
            formatted_answer += f"- **Source**: {source}, page: {page}: {reasoning}\n"

    ai_message = AIMessage(content=formatted_answer)

    logger.debug(f"Response synthesis result: {formatted_answer}")

    return {
        "messages": [ai_message],
        "answer": formatted_answer,
        "reasoning": (
            f"Synthesized response from {len(state.docs)} documents with proper "
            "citations"
        ),
    }
