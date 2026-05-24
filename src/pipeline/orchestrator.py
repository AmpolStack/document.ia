"""Pipeline orchestrator — coordinates the full documentation generation flow."""

import sys
import logging
from pathlib import Path

from src.config.settings import SCHEMA_PATH
from src.config.models import AUDIENCES
from src.docs.schema import load_schema
from src.docs.inventory import get_inventory, compact_inventory
from src.git.diff import get_structured_diff, format_diff_for_prompt
from src.llm.prompt import build_prompt
from src.llm.client import decide_actions
from src.rag.setup import configure as configure_rag
from src.rag.indexer import is_collection_empty, index_directory
from src.rag.retriever import query_relevant_context
from src.pipeline.executor import execute_actions

logger = logging.getLogger(__name__)


def run() -> None:
    """Execute the full documentation generation pipeline."""

    # 1. Load schema & initialize RAG
    load_schema(SCHEMA_PATH, ensure=True)
    configure_rag()
    logger.info("Pipeline started")

    # 2. Detect changes
    changes = get_structured_diff()
    if not changes:
        logger.info("No changes detected in src/. Exiting.")
        sys.exit(0)

    diff_text = format_diff_for_prompt(changes)
    logger.info("Files modified: %d", len(changes))

    # 3. Process each audience
    contexts: dict[str, str] = {}
    inventories: dict[str, str] = {}

    for audit in AUDIENCES:
        audit_path = Path(audit.path)
        audit_path.mkdir(parents=True, exist_ok=True)

        logger.info("Audience: %s (path: %s)", audit.label, audit.path)

        if is_collection_empty(audit.label):
            logger.info("Indexing %s documentation...", audit.label)
            index_directory(audit.label, audit.path)

        contexts[audit.label] = query_relevant_context(diff_text, audience=audit.label)
        inventory = get_inventory(audit_path, audit.label)
        inventories[audit.label] = compact_inventory(inventory)

        logger.info("  context=%d chars, inventory=%d files",
                     len(contexts[audit.label]), len(inventory))

    # 4. Ask LLM
    prompt = build_prompt(diff_text, contexts, inventories)
    actions = decide_actions(prompt)

    if not actions:
        logger.info("No documentation changes required. Exiting.")
        sys.exit(0)

    # 5. Execute actions
    generated = execute_actions(actions)

    logger.info("Pipeline completed. Files generated/updated: %d", len(generated))
