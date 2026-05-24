"""Query the vector store for relevant documentation context."""

import logging

from src.config.settings import RAG_TOP_K, RAG_SCORE_THRESHOLD
from llama_index.core import VectorStoreIndex
from src.rag.indexer import get_chroma_collection

logger = logging.getLogger(__name__)


def query_relevant_context(
    query: str, audience: str, n_results: int = RAG_TOP_K
) -> str:
    """Retrieve semantically relevant documentation chunks for a query.

    The query is typically a formatted git diff. Returned text is later embedded
    into the LLM prompt as evidence of what the project already documents.

    Args:
        query: Search text, usually the formatted code diff.
        audience: Documentation audience (e.g. ``"developer"``).
        n_results: Maximum number of candidate chunks to inspect.

    Returns:
        Concatenated relevant chunks, or an empty string when nothing useful is found.
    """
    logger.info("Searching context for '%s'...", audience)

    try:
        vector_store, _ = get_chroma_collection(audience)
        chroma_collection = vector_store._collection

        if chroma_collection.count() == 0:
            logger.info("No documents indexed for '%s'", audience)
            return ""

        index = VectorStoreIndex.from_vector_store(vector_store)
        retriever = index.as_retriever(
            similarity_top_k=n_results,
            vector_store_query_mode="default",
        )

        nodes = retriever.retrieve(query)

        if not nodes:
            logger.info("No relevant results for '%s'", audience)
            return ""

        relevant_texts = []
        for node in nodes:
            score = node.score if hasattr(node, "score") else 1.0
            if score > RAG_SCORE_THRESHOLD:
                relevant_texts.append(node.text)
                logger.info("  Score=%.3f: %s...", score, node.text[:100])

        if not relevant_texts:
            logger.info("Retrieved chunks do not exceed relevance threshold")
            return ""

        logger.info("Found %d relevant chunks", len(relevant_texts))
        return "\n\n---\n\n".join(relevant_texts)

    except Exception as e:
        logger.error("Error querying: %s", e)
        return ""
