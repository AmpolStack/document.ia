"""Initialize LlamaIndex global settings for the RAG pipeline.

This module is imported once by ``rag/__init__.py`` and configures the shared
LLM client, embedding model, and text splitter used across the project.
"""

import logging

from src.config.settings import (
    LLM_API_KEY,
    LLM_MODEL,
    LLM_BASE_URL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    EMBED_MODEL,
    EMBED_BATCH_SIZE,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)

from llama_index.core import Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike

logger = logging.getLogger(__name__)


def configure() -> None:
    """Configure LlamaIndex runtime settings.

    Must be called once before using any RAG functionality.
    Raises ValueError if LLM_API_KEY is not set.
    """
    if not LLM_API_KEY:
        raise ValueError(
            "LLM_API_KEY environment variable is not set or is empty. "
            "Please add it to your .env file."
        )

    Settings.llm = OpenAILike(
        model=LLM_MODEL,
        api_key=LLM_API_KEY,
        api_base=LLM_BASE_URL,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
        is_chat_model=True,
    )

    Settings.embed_model = HuggingFaceEmbedding(
        model_name=EMBED_MODEL,
        embed_batch_size=EMBED_BATCH_SIZE,
    )

    Settings.text_splitter = SentenceSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    logger.info(
        "RAG configured: llm=%s embed=%s chunk=%d",
        LLM_MODEL, EMBED_MODEL, CHUNK_SIZE,
    )
