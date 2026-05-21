"""RAG (Retrieval-Augmented Generation) manager for documentation indexing and retrieval.

This module handles the indexing of documentation files into a vector store (ChromaDB)
and provides semantic search capabilities for retrieving relevant documentation context
based on code changes.
"""

import os
from pathlib import Path
import re
from typing import List

from src.config import (
    LLM_MODEL,
    LLM_API_KEY,
    LLM_BASE_URL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    EMBED_MODEL,
    EMBED_BATCH_SIZE,
    VECTOR_STORE_PATH,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    RAG_TOP_K,
    RAG_SCORE_THRESHOLD,
)

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    Document,
    Settings,
    SimpleDirectoryReader,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike

import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore


def configure_llamaindex():
    """Configure global LlamaIndex settings.

    Initializes the LLM, embedding model, and text splitter with
    predefined configurations. This should be called once on module import.
    """
    if not LLM_API_KEY:
        raise ValueError(
            "DEEPSEEK_API_KEY environment variable is not set or is empty. "
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


def _get_chroma_collection(audience: str):
    """Retrieve or create a ChromaDB collection for a specific audience.

    Args:
        audience: Documentation type ('dev' for developers, 'user' for end users)

    Returns:
        Tuple of (ChromaVectorStore, collection_name)
    """
    collection_name = f"docs_{audience}"
    chroma_client = chromadb.PersistentClient(path=VECTOR_STORE_PATH)
    chroma_collection = chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    return vector_store, collection_name


def _chunk_markdown_smart(text: str) -> List[str]:
    """Divide markdown into smart chunks respecting document structure.

    Prioritizes sectioning (##) over strict size limits to maintain context.

    Args:
        text: Full content of markdown file

    Returns:
        List of text chunks
    """
    sections = re.split(r"(?=^##\s)", text, flags=re.MULTILINE)
    chunks = []

    for section in sections:
        if not section.strip():
            continue

        if len(section) <= CHUNK_SIZE * 2:
            chunks.append(section.strip())
        else:
            splitter = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
            sub_chunks = splitter.split_text(section)
            chunks.extend(sub_chunks)

    return chunks


def index_docs(audience: str, filepath: str, replace: bool = True) -> None:
    """Index a markdown file into the vector store.

    If replace=True, removes previous nodes for the same file before indexing.

    Args:
        audience: Documentation type ('dev' or 'user')
        filepath: Path to the markdown file to index
        replace: Whether to replace existing entries for this file (default: True)
    """
    if not os.path.exists(filepath):
        print(f"[rag] Note: {filepath} does not exist, will be indexed when generated.")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip():
        print(f"[rag] Note: {filepath} is empty, nothing to index.")
        return

    if replace:
        delete_docs_by_source(audience, filepath)

    vector_store, collection_name = _get_chroma_collection(audience)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    documents = [
        Document(
            text=content,
            metadata={
                "source": filepath,
                "audience": audience,
                "filename": os.path.basename(filepath)
            }
        )
    ]

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        transformations=[SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)]
    )

    num_nodes = len(index.docstore.docs)
    print(f"[rag] Indexed {num_nodes} nodes from '{filepath}' for audience '{audience}'")


def index_directory(audience: str, directory: str) -> None:
    """Index all markdown files in a directory.

    Useful for initial loading of existing documentation.

    Args:
        audience: Documentation type ('dev' or 'user')
        directory: Path to directory containing markdown files
    """
    if not os.path.exists(directory):
        print(f"[rag] Directory {directory} does not exist")
        return

    md_files = list(Path(directory).rglob("*.md"))
    if not md_files:
        print(f"[rag] No markdown files found in {directory}")
        return

    print(f"[rag] Indexing {len(md_files)} files from {directory}...")
    for md_file in md_files:
        index_docs(audience, str(md_file))


def is_collection_empty(audience: str) -> bool:
    """Check if a documentation collection has been indexed yet.

    Args:
        audience: Documentation type ('dev' or 'user')

    Returns:
        True if collection is empty, False otherwise
    """
    try:
        vector_store, _ = _get_chroma_collection(audience)
        chroma_collection = vector_store._collection
        count = chroma_collection.count()
        return count == 0
    except Exception:
        return True


def query_relevant_context(query: str, audience: str, n_results: int = RAG_TOP_K) -> str:
    """Retrieve relevant documentation chunks based on semantic similarity.

    Uses LlamaIndex for semantic search across the vector store.

    Args:
        query: Search text (usually the code diff)
        audience: Documentation type ('dev' or 'user')
        n_results: Maximum number of chunks to retrieve (default: 3)

    Returns:
        String with relevant chunks concatenated, or empty string if no results
    """
    print(f"[rag] Searching context for '{audience}'...")

    try:
        vector_store, collection_name = _get_chroma_collection(audience)
        chroma_collection = vector_store._collection
        if chroma_collection.count() == 0:
            print(f"[rag] No documents indexed for '{audience}'")
            return ""

        index = VectorStoreIndex.from_vector_store(vector_store)
        retriever = index.as_retriever(
            similarity_top_k=n_results,
            vector_store_query_mode="default"
        )

        nodes = retriever.retrieve(query)

        if not nodes:
            print(f"[rag] No relevant results for '{audience}'")
            return ""

        relevant_texts = []
        for node in nodes:
            score = node.score if hasattr(node, 'score') else 1.0
            if score > RAG_SCORE_THRESHOLD:
                relevant_texts.append(node.text)
                print(f"[rag]   Score={score:.3f}: {node.text[:100]}...")

        if not relevant_texts:
            print(f"[rag] Retrieved chunks do not exceed relevance threshold")
            return ""

        print(f"[rag] Found {len(relevant_texts)} relevant chunks")
        return "\n\n---\n\n".join(relevant_texts)

    except Exception as e:
        print(f"[rag] Error querying: {str(e)}")
        return ""


def update_index_after_generation(paths: List[str]) -> None:
    """Re-index generated files, replacing old versions.

    Args:
        paths: List of file paths to index
    """
    for path in paths:
        if "dev" in path.lower() or "api" in path.lower() or "developer" in path.lower():
            audience = "dev"
        elif "user" in path.lower() or "guide" in path.lower():
            audience = "user"
        else:
            print(f"[rag] Could not determine audience for '{path}', using 'dev' as default")
            audience = "dev"

        index_docs(audience, path, replace=True)


def delete_docs_by_source(audience: str, source_path: str) -> int:
    """Delete all indexed nodes with metadata source matching source_path.

    Args:
        audience: Documentation type ('dev' or 'user')
        source_path: Source file path to delete

    Returns:
        Number of nodes deleted
    """
    vector_store, collection_name = _get_chroma_collection(audience)
    chroma_collection = vector_store._collection

    try:
        results = chroma_collection.get(
            where={"source": source_path},
            include=["metadatas"]
        )
        ids_to_delete = results['ids']
        if ids_to_delete:
            chroma_collection.delete(ids=ids_to_delete)
            print(f"[rag] Deleted {len(ids_to_delete)} old nodes from {source_path}")
        return len(ids_to_delete)
    except Exception as e:
        print(f"[rag] Error deleting {source_path}: {e}")
        return 0


configure_llamaindex()

print(f"[rag] RAG Manager initialized")
print(f"[rag]    LLM: {LLM_MODEL}")
print(f"[rag]    Embeddings: {EMBED_MODEL}")
print(f"[rag]    Vector Store: {VECTOR_STORE_PATH}")
print(f"[rag]    Chunk size: {CHUNK_SIZE}")
