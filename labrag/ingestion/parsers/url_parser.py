from firecrawl import FirecrawlApp
from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate
from loguru import logger

from labrag.ingestion.parsers.models import URLParseResult


class URLParser:
    """Parse URLs using Firecrawl - returns raw content for chunking"""

    def __init__(self) -> None:
        """Initialize the URL parser"""
        self.firecrawl = FirecrawlApp()

    async def parse(self, url: str, clean_article: bool = True) -> URLParseResult:
        """Parse URL and return structured result

        Args:
            url: The URL to parse
            clean_article: Whether to clean the article

        Returns:
            URLParseResult: The parsed document with raw content and metadata
        """

        logger.info(f"Parsing URL: {url}")

        # Note: Firecrawl doesn't have async support yet, but we prepare for it
        result = self.firecrawl.scrape_url(url, formats=["markdown"], timeout=60_000)

        if not result.markdown:
            logger.warning(f"No content extracted from {url}")
            return None

        content = result.markdown
        if clean_article:
            logger.info(f"Cleaning article for {url}")
            content = await self._clean_article(content)

        metadata = {
            "source": url,
            "source_type": "url",
            "title": result.metadata.get("title", "").strip(),
            "parsing_method": "firecrawl",
        }

        return URLParseResult(
            content=content,
            raw_content=result.markdown,
            metadata=metadata,
        )

    async def _clean_article(self, markdown: str) -> str:
        """Clean article using LLM

        Args:
            markdown: The markdown content to clean

        Returns:
            str: The cleaned markdown content
        """
        system_message = """
        You are a helpful assistant that rewrites markdown articles by removing ADs and non-relevant content.

        You should identify the relevant content of the article, including title, subtitles, metadata, 
        paragraphs, figures, captions, etc., and return ONLY the relevant content in markdown format.
        If no relevant content is identified, return an empty string.
        """  # noqa: E501, W291

        prompt = ChatPromptTemplate(
            [("system", system_message), ("human", "{markdown}")]
        )

        llm = init_chat_model("gpt-4o")
        chain = prompt | llm
        cleaned = await chain.ainvoke(input={"markdown": markdown})

        return cleaned.content
