"""Index and manage documents in the ChromaDB vector store."""

import os
from pathlib import Path
from typing import List
import logging

from src.config.settings import VECTOR_STORE_PATH, CHUNK_SIZE, CHUNK_OVERLAP

from llama_index.core import VectorStoreIndex, StorageContext, Document
from llama_index.core.node_parser import SentenceSplitter
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore

logger = logging.getLogger(__name__)


# ── Connection ──────────────────────────────────────────────────────────────


def get_chroma_collection(audience: str):
    """Retrieve or create the ChromaDB collection for a documentation audience.

    Args:
        audience: Documentation audience label (e.g. ``"developer"``).

    Returns:
        Tuple of ``(vector_store, collection_name)``.
    """
    collection_name = f"docs_{audience}"
    chroma_client = chromadb.PersistentClient(path=VECTOR_STORE_PATH)
    chroma_collection = chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    return vector_store, collection_name


# ── Indexing ────────────────────────────────────────────────────────────────


def index_docs(audience: str, filepath: str, replace: bool = True) -> None:
    """Index a single markdown file into the vector store.

    When ``replace`` is True, previously indexed nodes for the same source path
    are removed first so the vector store reflects current file contents.

    Args:
        audience: Documentation audience (e.g. ``"developer"``).
        filepath: Markdown file path to index.
        replace: Whether to remove older index entries for the same file.
    """
    if not os.path.exists(filepath):
        logger.info("Note: %s does not exist, will be indexed when generated.", filepath)
        return

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        logger.info("Note: %s is empty, nothing to index.", filepath)
        return

    if replace:
        delete_docs_by_source(audience, filepath)

    vector_store, _ = get_chroma_collection(audience)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    documents = [
        Document(
            text=content,
            metadata={
                "source": filepath,
                "audience": audience,
                "filename": os.path.basename(filepath),
            },
        )
    ]

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        transformations=[
            SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        ],
    )

    num_nodes = len(index.docstore.docs)
    logger.info(
        "Indexed %d nodes from '%s' for audience '%s'", num_nodes, filepath, audience
    )


def index_directory(audience: str, directory: str) -> None:
    """Index all markdown files in a directory.

    Useful for initial loading of existing documentation.

    Args:
        audience: Audience label (e.g. ``"developer"``).
        directory: Path to directory containing markdown files.
    """
    if not os.path.exists(directory):
        logger.info("Directory %s does not exist", directory)
        return

    md_files = list(Path(directory).rglob("*.md"))
    if not md_files:
        logger.info("No markdown files found in %s", directory)
        return

    logger.info("Indexing %d files from %s...", len(md_files), directory)
    for md_file in md_files:
        index_docs(audience, str(md_file))


# ── Status ──────────────────────────────────────────────────────────────────


def is_collection_empty(audience: str) -> bool:
    """Check if a documentation collection has been indexed yet.

    Returns:
        True if collection is empty, False otherwise.
    """
    try:
        vector_store, _ = get_chroma_collection(audience)
        chroma_collection = vector_store._collection
        count = chroma_collection.count()
        return count == 0
    except Exception:
        return True


# ── Update / cleanup ────────────────────────────────────────────────────────


def update_index_after_generation(paths: List[str]) -> None:
    """Re-index generated files, replacing old versions.

    Args:
        paths: List of file paths to index.
    """
    for path in paths:
        if "dev" in path.lower() or "api" in path.lower() or "developer" in path.lower():
            audience = "dev"
        elif "user" in path.lower() or "guide" in path.lower():
            audience = "user"
        else:
            logger.warning("Could not determine audience for '%s', using 'dev'", path)
            audience = "dev"

        index_docs(audience, path, replace=True)


def delete_docs_by_source(audience: str, source_path: str) -> int:
    """Delete all indexed nodes with metadata source matching source_path.

    Args:
        audience: Audience label.
        source_path: Source file path to delete from the index.

    Returns:
        Number of nodes deleted.
    """
    vector_store, _ = get_chroma_collection(audience)
    chroma_collection = vector_store._collection

    try:
        results = chroma_collection.get(
            where={"source": source_path}, include=["metadatas"]
        )
        ids_to_delete = results["ids"]
        if ids_to_delete:
            chroma_collection.delete(ids=ids_to_delete)
            logger.info("Deleted %d old nodes from %s", len(ids_to_delete), source_path)
        return len(ids_to_delete)
    except Exception as e:
        logger.error("Error deleting %s: %s", source_path, e)
        return 0
