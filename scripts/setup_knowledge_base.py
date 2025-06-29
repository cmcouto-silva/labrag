#!/usr/bin/env python3
"""Setup LabRAG Knowledge Base"""

import argparse
import asyncio

from labrag.ingestion.knowledge_base import KnowledgeBaseBuilder


async def main() -> int | None:
    parser = argparse.ArgumentParser(description="Setup LabRAG knowledge base")
    parser.add_argument(
        "--config", default="configs/default.yml", help="Config file path"
    )
    parser.add_argument("--force", action="store_true", help="Force reprocessing")

    args = parser.parse_args()

    try:
        builder = KnowledgeBaseBuilder()
        await builder.build_from_config(args.config, force=args.force)

    except Exception:
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
