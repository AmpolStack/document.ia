"""Execute LLM-decided actions on the filesystem."""

import logging
from pathlib import Path
from typing import List

from src.rag.indexer import delete_docs_by_source, update_index_after_generation

logger = logging.getLogger(__name__)


def execute_actions(actions: List[dict]) -> List[str]:
    """Apply create, update, and delete actions to the documentation tree.

    Args:
        actions: List of action dicts from the LLM.

    Returns:
        List of file paths that were created or updated.
    """
    generated_files: List[str] = []

    for action in actions:
        action_type = action.get("type")
        audience = action.get("audience")
        file_path = Path(action.get("file"))
        content = action.get("content", "")

        # Security: prevent writing outside docs/
        if not str(file_path).startswith("docs/"):
            logger.warning("Unsafe path ignored: %s", file_path)
            continue

        if action_type in ("create", "update"):
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            logger.info("%s %s", action_type.upper(), file_path)
            generated_files.append(str(file_path))

        elif action_type == "delete":
            if file_path.exists():
                file_path.unlink()
                logger.info("DELETE %s", file_path)
                delete_docs_by_source(audience, str(file_path))
            else:
                logger.info("DELETE skipped: %s does not exist", file_path)

        else:
            logger.warning("Unknown action type '%s' for %s", action_type, file_path)

    if generated_files:
        logger.info("Updating vector store...")
        update_index_after_generation(generated_files)

    return generated_files
