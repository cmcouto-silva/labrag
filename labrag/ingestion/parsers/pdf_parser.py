from pathlib import Path

from agentic_doc.parse import parse

from labrag.ingestion.parsers.models import PDFParseResult


class PDFParser:
    """Parse PDFs using LandingAI - returns pre-chunked content"""

    def parse(self, pdf_path: str | Path) -> PDFParseResult:
        """Parse PDF and return structured result

        Args:
            pdf_path: The path to the PDF file to parse

        Returns:
            PDFParseResult: The parsed document with chunks and metadata
        """
        parsed_docs = parse(
            pdf_path,
            include_marginalia=False,
            include_metadata_in_markdown=False,
        )

        # Extract chunks with metadata
        chunks = []

        for chunk in parsed_docs[0].chunks:
            chunk_data = {
                "content": chunk.text,
                "page": chunk.grounding[0].page + 1,
            }
            chunks.append(chunk_data)

        metadata = {
            "source": Path(pdf_path).name,
            "source_type": "pdf",
            "total_chunks": len(chunks),
            "parsing_method": "landing_ai",
        }

        return PDFParseResult(
            content=parsed_docs[0].markdown, metadata=metadata, chunks=chunks
        )
