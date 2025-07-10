#!/usr/bin/env python3
"""Setup LabRAG Knowledge Base"""

import argparse
import asyncio
import traceback

import dotenv
from loguru import logger

from labrag.ingestion.knowledge_base import KnowledgeBaseBuilder

dotenv.load_dotenv()


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

    except Exception as e:
        logger.error(f"Error: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
