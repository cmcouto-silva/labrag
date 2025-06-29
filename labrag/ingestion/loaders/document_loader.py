from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from loguru import logger

from labrag.ingestion.loaders.vector_store import VectorStore
from labrag.ingestion.parsers.models import PDFParseResult, URLParseResult


class DocumentLoader:
    """Load parsed documents into vector store with cosine similarity"""

    def __init__(
        self,
        vector_store: VectorStore,
        chunk_size: int = 5000,
        chunk_overlap: int = 200,
    ) -> None:
        self.vector_store = vector_store

        # Text splitter for URLs (PDFs come pre-chunked from LandingAI)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def load_pdf_result(self, pdf_result: PDFParseResult) -> bool:
        """Load PDF chunks (already chunked by LandingAI)"""
        try:
            documents = []

            for i, chunk in enumerate(pdf_result.chunks):
                # Prepare metadata
                metadata = pdf_result.metadata.copy()
                target_keys = ["source", "source_type", "source_url", "parsing_method"]
                filtered_metadata = {
                    k: v for k, v in metadata.items() if k in target_keys
                }
                filtered_metadata.update(
                    {
                        "page": chunk["page"],
                        "chunk_index": i,
                        "total_chunks": len(pdf_result.chunks),
                    }
                )

                # Create LangChain Document with metadata
                doc = Document(
                    id=f"{i}-{pdf_result.metadata['source']}",
                    page_content=chunk["content"],
                    metadata=filtered_metadata,
                )
                documents.append(doc)

            # Add documents to vector store
            self.vector_store.add_documents(documents)
            logger.success(
                f"Loaded {len(documents)} PDF chunks from "
                f"{pdf_result.metadata['source']}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to load PDF: {e}")
            return False

    def load_url_result(self, url_result: URLParseResult) -> bool:
        """Load URL content (needs chunking with text splitter)"""
        try:
            # Split content into chunks
            text_chunks = self.text_splitter.split_text(url_result.content)

            documents = []
            for i, chunk_text in enumerate(text_chunks):
                # Prepare    metadata
                metadata = url_result.metadata.copy()
                metadata.update(
                    {
                        "chunk_index": i,
                        "total_chunks": len(text_chunks),
                    }
                )

                # Create LangChain Document with metadata
                doc = Document(
                    id=f"{i}-{url_result.metadata['source']}",
                    page_content=chunk_text,
                    metadata=metadata,
                )
                documents.append(doc)

            # Add documents to vector store
            self.vector_store.add_documents(documents)
            logger.success(
                f"Loaded {len(documents)} URL chunks from "
                f"{url_result.metadata['source']}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to load URL: {e}")
            return False
