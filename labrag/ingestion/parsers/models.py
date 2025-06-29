from typing import Any

from pydantic import BaseModel


class ParsedDocument(BaseModel):
    """Base model for parsed document content"""

    content: str
    metadata: dict[str, Any]


class PDFParseResult(ParsedDocument):
    """Result from PDF parsing with LandingAI chunks"""

    chunks: list[dict[str, Any]]  # Pre-chunked from LandingAI


class URLParseResult(ParsedDocument):
    """Result from URL parsing with Firecrawl"""

    raw_content: str
