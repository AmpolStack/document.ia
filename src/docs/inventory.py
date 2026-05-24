"""Inventory of existing documentation files."""

from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def get_inventory(base_path: Path, label: str) -> dict[str, str]:
    """Collect all markdown files from a documentation directory.

    Args:
        base_path: Root directory path for documentation.
        label: Human-readable label for the documentation type.

    Returns:
        Dictionary mapping file paths to file contents.
    """
    logger.info(f"Reading {label} documentation from {base_path}")

    if not base_path.exists():
        logger.warning(f"Directory {base_path} does not exist.")
        return {}

    tree: dict[str, str] = {}
    for path in base_path.rglob("*.md"):
        content = path.read_text(encoding="utf-8")
        tree[str(path)] = content

    logger.info(f"Found {len(tree)} markdown file(s) in {label}")
    return tree


def compact_inventory(docs_tree: dict[str, str]) -> str:
    """Build a compact inventory string for the LLM prompt.

    Returns only file paths sorted alphabetically — the LLM uses this
    to know which files already exist before deciding to create new ones.
    """
    if not docs_tree:
        return ""
    sorted_files = sorted(docs_tree.keys())
    return "\n".join(sorted_files)


if __name__ == "__main__":
    logger.info("Developer Docs Inventory:")
    dev_inventory = get_inventory(Path("../../docs/dev"), "Developer")
    logger.info(compact_inventory(dev_inventory))
    logger.info("User Docs Inventory:")
    user_inventory = get_inventory(Path("docs/user"), "User")
    logger.info(compact_inventory(user_inventory))
