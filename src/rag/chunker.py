"""Markdown-aware text chunking for RAG indexing.

Prefer section boundaries (``##`` headings) over uniform splitting
so retrieved snippets remain meaningful to the LLM.
"""

import re
from typing import List

from src.config.settings import CHUNK_SIZE, CHUNK_OVERLAP
from llama_index.core.node_parser import SentenceSplitter


def chunk_markdown(text: str) -> List[str]:
    """Split markdown text into retrieval-aware chunks.

    Args:
        text: Full content of a markdown file.

    Returns:
        List of text chunks respecting section boundaries.
    """
    sections = re.split(r"(?=^##\s)", text, flags=re.MULTILINE)
    chunks: List[str] = []

    for section in sections:
        if not section.strip():
            continue

        if len(section) <= CHUNK_SIZE * 2:
            chunks.append(section.strip())
        else:
            splitter = SentenceSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
            )
            chunks.extend(splitter.split_text(section))

    return chunks
