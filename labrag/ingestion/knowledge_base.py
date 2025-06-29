# labrag/ingestion/builder.py

import asyncio
import glob
import hashlib
import os
from typing import Any

from loguru import logger

from labrag.config import load_config
from labrag.ingestion.loaders.document_loader import DocumentLoader
from labrag.ingestion.loaders.vector_store import VectorStore
from labrag.ingestion.parsers.cache import DocumentCache
from labrag.ingestion.parsers.pdf_parser import PDFParser
from labrag.ingestion.parsers.url_parser import URLParser


class KnowledgeBaseBuilder:
    """Build knowledge base with cosine similarity using text-embedding-3-small"""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}

        # Initialize components
        vector_store_config = self.config.get("vector_store", {})
        store_path = vector_store_config.get("store_path", "data/vector_store")

        # Vector store with cosine similarity
        self.vector_store = VectorStore(store_path)

        # Document loader
        self.document_loader = DocumentLoader(
            self.vector_store,
            chunk_size=vector_store_config.get("chunk_size", 5000),
            chunk_overlap=vector_store_config.get("chunk_overlap", 200),
        )

        # Parsers and cache
        self.pdf_parser = PDFParser()
        self.url_parser = URLParser()
        self.cache = DocumentCache()

    async def build_from_config(self, config_path: str, force: bool = False) -> int:
        """Build knowledge base from configuration file"""
        config = load_config(config_path)
        processed_count = 0

        logger.info("Starting knowledge base build...")

        # Process PDFs from papers directory
        data_sources = config.get("data_sources", {})
        papers_dir = data_sources.get("papers_dir", "data/raw/papers")

        # Get PDF files from the papers directory
        pdf_files = []
        if os.path.exists(papers_dir):
            pdf_files = glob.glob(os.path.join(papers_dir, "*.pdf"))

        logger.info(f"Processing {len(pdf_files)} PDF files from {papers_dir}")
        for pdf_path in pdf_files:
            if self._process_pdf(pdf_path, force):
                processed_count += 1

        # Process URLs from media_urls - use async for better performance
        urls = data_sources.get("media_urls", [])
        logger.info(f"Processing {len(urls)} URLs")

        # Process URLs concurrently for better performance
        url_tasks = [self._process_url_async(url, force) for url in urls]
        if url_tasks:
            url_results = await asyncio.gather(*url_tasks, return_exceptions=True)
            for result in url_results:
                if isinstance(result, bool) and result:
                    processed_count += 1
                elif isinstance(result, Exception):
                    logger.error(f"Error processing URL: {result}")

        logger.success(
            f"Knowledge base build complete: {processed_count} documents processed"
        )
        return processed_count

    def _process_pdf(self, pdf_path: str, force: bool = False) -> bool:
        """Process single PDF file"""
        doc_id = hashlib.sha256(pdf_path.encode()).hexdigest()

        if not force and self.cache.is_processed(doc_id):
            logger.debug(f"PDF {pdf_path} already processed")
            return False

        logger.info(f"Processing PDF: {pdf_path}")
        pdf_result = self.pdf_parser.parse(pdf_path)
        if not pdf_result:
            logger.error(f"Failed to parse PDF: {pdf_path}")
            return False

        success = self.document_loader.load_pdf_result(pdf_result)
        if success:
            self.cache.add_document(doc_id, pdf_path, "pdf")
            logger.info(f"Successfully processed PDF: {pdf_path}")

        return success

    async def _process_url_async(self, url: str, force: bool = False) -> bool:
        """Process single URL asynchronously"""
        doc_id = hashlib.sha256(url.encode()).hexdigest()

        if not force and self.cache.is_processed(doc_id):
            logger.debug(f"URL {url} already processed")
            return False

        logger.info(f"Processing URL: {url}")
        try:
            url_result = await self.url_parser.parse(url)
            if not url_result:
                logger.error(f"Failed to parse URL: {url}")
                return False

            success = self.document_loader.load_url_result(url_result)
            if success:
                self.cache.add_document(doc_id, url, "url")
                logger.info(f"Successfully processed URL: {url}")

            return success
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            return False

    def _process_url(self, url: str, force: bool = False) -> bool:
        """Process single URL (sync version for backward compatibility)"""
        return asyncio.run(self._process_url_async(url, force))
