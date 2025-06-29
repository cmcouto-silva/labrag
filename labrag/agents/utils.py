"""Utility functions for the agentic workflow."""

from collections import defaultdict

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage


def get_chat_history(messages: list[BaseMessage], last_n_messages: int = 10) -> str:
    """Get the chat history from the messages."""
    return "\n".join(
        [
            f"{msg.type.capitalize()}: {msg.content}"
            for msg in messages[-last_n_messages - 1 : -1]
        ]
    )


def format_document_context(docs: list[Document]) -> str:
    """
    Format documents with source and content.

    Args:
        docs: List of documents with metadata containing 'source' and optionally 'page'

    Returns:
        Complete formatted context string with all documents like:
        - Document 1 (Source: source): {content}
        - Document 2 (Source: source - page N): {content}
    """
    formatted_docs = []

    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page")

        if page is not None:
            header = f"Document {i + 1} (Source: {source} - page {page})"
        else:
            header = f"Document {i + 1} (Source: {source})"

        formatted_docs.append(f"{header}:\n{doc.page_content}")

    return "\n\n".join(formatted_docs)


def format_sources_with_pages(docs: list[Document]) -> list[str]:
    """
    Format document sources with page information.

    Args:
        docs: List of documents with metadata containing 'source' and optionally 'page'

    Returns:
        List of formatted strings like:
        - "sciadv.abo0234.pdf — pages 1,2,3" for sources with pages
        - "example.com/article" for sources without pages
    """
    # Group documents by source and collect pages
    source_pages = defaultdict(set)

    for doc in docs:
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page")

        if page is not None:
            source_pages[source].add(page)
        else:
            # Ensure source is in dict even without pages
            if source not in source_pages:
                source_pages[source] = set()

    # Format the output
    formatted_sources = []
    for source, pages in source_pages.items():
        if pages:
            # Sort pages numerically and format
            sorted_pages = sorted(pages)
            pages_str = ",".join(map(str, sorted_pages))
            formatted_sources.append(f"{source} — pages {pages_str}")
        else:
            # No pages, just the source
            formatted_sources.append(source)

    return formatted_sources
