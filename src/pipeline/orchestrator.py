import json
import os
import sys
import logging
from pathlib import Path

from src.config.settings import SCHEMA_PATH, PIPELINE_STATE_PATH
from src.config.models import AUDIENCES
from src.docs.schema import load_schema
from src.docs.inventory import get_inventory, compact_inventory
from src.git.diff import get_structured_diff, format_diff_for_prompt, resolve_diff_base, get_current_head
from src.llm.prompt import build_prompt
from src.llm.client import decide_actions
from src.rag.setup import configure as configure_rag
from src.rag.indexer import is_collection_empty, index_directory
from src.rag.retriever import query_relevant_context
from src.pipeline.executor import execute_actions

logger = logging.getLogger(__name__)


def _load_last_commit() -> str | None:
    if PIPELINE_STATE_PATH.exists():
        data = json.loads(PIPELINE_STATE_PATH.read_text())
        return data.get("last_commit")
    return None


def _save_last_commit(commit_hash: str) -> None:
    PIPELINE_STATE_PATH.write_text(json.dumps({"last_commit": commit_hash}, indent=2))
    logger.info("Saved pipeline state: last_commit=%s", commit_hash[:8])


def run() -> None:
    load_schema(SCHEMA_PATH, ensure=True)
    configure_rag()
    logger.info("Pipeline started")

    last_commit = _load_last_commit()
    base_ref = os.getenv("DIFF_BASE_REF") or resolve_diff_base(last_commit)
    if base_ref is None:
        logger.info("HEAD already processed. Exiting.")
        sys.exit(0)

    changes = get_structured_diff(base_ref=base_ref)
    if not changes:
        logger.info("No changes detected in src/. Exiting.")
        sys.exit(0)

    diff_text = format_diff_for_prompt(changes)
    logger.info("Files modified: %d", len(changes))

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

    prompt = build_prompt(diff_text, contexts, inventories)
    actions = decide_actions(prompt)

    if not actions:
        logger.info("No documentation changes required. Exiting.")
        sys.exit(0)

    generated = execute_actions(actions)
    _save_last_commit(get_current_head())

    logger.info("Pipeline completed. Files generated/updated: %d", len(generated))
