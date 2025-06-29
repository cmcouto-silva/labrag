# labrag/ingestion/loaders/vector_store.py

from pathlib import Path
from typing import Any

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.vectorstores.base import VectorStoreRetriever
from langchain_openai import OpenAIEmbeddings
from loguru import logger


class VectorStore:
    """LangChain FAISS wrapper for vector storage"""

    def __init__(self, store_path: str = "data/vector_store") -> None:
        """Initialize the vector store

        Args:
            store_path: The path to the vector store
        """
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.store_path = Path(store_path)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.vector_store: FAISS | None = None
        self.load()

    def add_documents(self, documents: list[Document]) -> None:
        """Add LangChain documents to vector store

        Args:
            documents: List of LangChain documents to add to the vector store
        """
        if not documents:
            return

        if self.vector_store is None:
            # Create new vector store
            self.vector_store = FAISS.from_documents(
                documents, self.embeddings, distance_strategy="MAX_INNER_PRODUCT"
            )
            logger.info(f"Created vector store with {len(documents)} documents")
        else:
            # Add to existing vector store
            self.vector_store.add_documents(documents)
            logger.info(f"Added {len(documents)} documents to vector store")

        self.save()

    def search(self, query: str, k: int = 5) -> list[Document]:
        """Search and return LangChain Documents

        Args:
            query: The query to search for
            k: The number of documents to return

        Returns:
            list[Document]: The documents that match the query
        """
        if self.vector_store is None:
            logger.warning("No vector store available")
            return []

        return self.vector_store.similarity_search(query, k=k)

    async def asearch(self, query: str, k: int = 5) -> list[Document]:
        """Async search and return LangChain Documents

        Args:
            query: The query to search for
            k: The number of documents to return

        Returns:
            list[Document]: The documents that match the query
        """
        if self.vector_store is None:
            logger.warning("No vector store available")
            return []

        return await self.vector_store.asimilarity_search(query, k=k)

    def search_with_scores(
        self, query: str, k: int = 5
    ) -> list[tuple[Document, float]]:
        """Search and return documents with similarity scores

        Args:
            query: The query to search for
            k: The number of documents to return

        Returns:
            list[Document]: The documents that match the query
        """
        if self.vector_store is None:
            logger.warning("No vector store available")
            return []

        return self.vector_store.similarity_search_with_score(query, k=k)

    def as_retriever(self, **kwargs: dict[str, Any]) -> VectorStoreRetriever:
        """Get LangChain retriever for use in chains

        Args:
            **kwargs: Additional arguments to pass to the retriever

        Returns:
            Retriever: The retriever
        """
        if self.vector_store is None:
            logger.warning("No vector store available")
            return None
        return self.vector_store.as_retriever(**kwargs)

    def save(self) -> None:
        """Save to disk"""
        if self.vector_store is not None:
            self.vector_store.save_local(str(self.store_path))
            logger.debug(f"Saved vector store to {self.store_path}")

    def load(self) -> None:
        """Load from disk"""
        try:
            index_path = self.store_path / "index.faiss"
            if index_path.exists():
                self.vector_store = FAISS.load_local(
                    str(self.store_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True,
                )
                logger.info(f"Loaded existing vector store from {self.store_path}")
        except Exception as e:
            logger.info(f"No existing vector store found: {e}")
            self.vector_store = None
