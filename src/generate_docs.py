"""Main module for automatic documentation generation pipeline.

This module orchestrates the entire documentation generation workflow:
1. Analyzes git diffs for code changes
2. Queries existing documentation context
3. Uses LLM to decide documentation updates
4. Executes the decided actions (create, update, delete)
5. Updates the vector store with new documentation
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

import yaml

from src.config import SCHEMA_PATH, DEV_DOC_PATH, USER_DOC_PATH
from src.diff_parser import FileChange, format_diff_for_prompt, get_structured_diff
from src.llm_decider import decide_actions
from src.rag_manager import (
    query_relevant_context,
    is_collection_empty,
    index_directory,
    update_index_after_generation,
    delete_docs_by_source,
)

load_dotenv()


def load_schema() -> dict:
    """Load and parse the documentation schema.

    Returns:
        Dictionary containing the schema definition

    Raises:
        FileNotFoundError: If schema.yml does not exist
    """
    print(f"[generate_docs] Loading schema from {SCHEMA_PATH}")

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        schema = yaml.safe_load(f)

    print("[generate_docs] Schema loaded successfully.")
    return schema


def ensure_schema() -> None:
    """Ensure schema.yml exists, creating a default one if necessary."""
    if SCHEMA_PATH.exists():
        print(f"[generate_docs] Schema already exists at {SCHEMA_PATH}")
        return

    SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)

    default_schema = {
        "version": "1.0",
        "documentation": {
            "dev": {
                "description": "Developer-focused documentation",
                "sections": ["API Reference", "Architecture", "Setup", "Contributing"]
            },
            "user": {
                "description": "User-focused documentation",
                "sections": ["Getting Started", "User Guide", "FAQ", "Troubleshooting"]
            }
        }
    }

    with SCHEMA_PATH.open("w", encoding="utf-8") as f:
        yaml.dump(default_schema, f, default_flow_style=False)

    print(f"[generate_docs] Default schema created at {SCHEMA_PATH}")


def get_docs_tree(base_path: Path, label: str) -> dict[str, str]:
    """Collect all markdown files from a documentation directory.

    Args:
        base_path: Root directory path for documentation
        label: Human-readable label for the documentation type

    Returns:
        Dictionary mapping file paths to file contents
    """
    print(f"[generate_docs] Reading {label} documentation from {base_path}")

    if not base_path.exists():
        print(f"[generate_docs] Directory {base_path} does not exist.")
        return {}

    tree: dict[str, str] = {}
    for path in base_path.rglob("*.md"):
        content = path.read_text(encoding="utf-8")
        tree[str(path)] = content

    print(f"[generate_docs] Found {len(tree)} markdown file(s) in {label}")
    return tree


def build_docs_inventory(docs_tree: dict[str, str]) -> str:
    """Build a compact inventory string for the LLM prompt."""
    if not docs_tree:
        return ""
    sorted_files = sorted(docs_tree.keys())
    return "\n".join(sorted_files)


def main() -> None:
    """Execute the documentation generation pipeline.

    This function:
    1. Validates configuration and API keys
    2. Ensures schema exists
    3. Detects code changes
    4. Indexes existing documentation
    5. Queries LLM for documentation actions
    6. Executes the actions
    7. Updates vector store
    """
    print("[generate_docs] Starting automatic documentation pipeline")

    # Ensure schema exists
    ensure_schema()

    # Get code changes
    changes = get_structured_diff()
    if not changes:
        print("[generate_docs] No changes detected in src/. Exiting.")
        sys.exit(0)

    # Index existing documentation if first time
    if is_collection_empty("dev"):
        print("[generate_docs] Indexing developer documentation...")
        index_directory("dev", str(DEV_DOC_PATH))
    if is_collection_empty("user"):
        print("[generate_docs] Indexing user documentation...")
        index_directory("user", str(USER_DOC_PATH))

    # Prepare diff and context
    diff_text = format_diff_for_prompt(changes)
    dev_context = query_relevant_context(diff_text, audience="dev")
    user_context = query_relevant_context(diff_text, audience="user")

    dev_docs_tree = get_docs_tree(DEV_DOC_PATH, "developer")
    user_docs_tree = get_docs_tree(USER_DOC_PATH, "user")
    dev_docs_inventory = build_docs_inventory(dev_docs_tree)
    user_docs_inventory = build_docs_inventory(user_docs_tree)

    print("[generate_docs] Summary:")
    print(f"  - Files modified: {len(changes)}")
    print(f"  - Dev context: {len(dev_context)} characters")
    print(f"  - User context: {len(user_context)} characters")
    print(f"  - Dev docs inventory: {len(dev_docs_tree)} files")
    print(f"  - User docs inventory: {len(user_docs_tree)} files")

    # Decide actions with LLM
    try:
        actions = decide_actions(
            diff_text,
            dev_context,
            user_context,
            dev_docs_inventory,
            user_docs_inventory,
        )
    except json.JSONDecodeError as e:
        print(f"[generate_docs] LLM returned invalid JSON: {e}")
        sys.exit(0)
    except Exception as e:
        print(f"[generate_docs] Error deciding actions: {e}")
        sys.exit(1)

    if not actions:
        print("[generate_docs] LLM determined no documentation changes are required.")
        sys.exit(0)

    # Execute actions
    generated_files = []
    for action in actions:
        action_type = action.get("type")
        audience = action.get("audience")
        file_path = Path(action.get("file"))
        content = action.get("content", "")

        # Validate path is within docs/ (security check)
        if not str(file_path).startswith("docs/"):
            print(f"[generate_docs] Unsafe path ignored: {file_path}")
            continue

        if action_type in ("create", "update"):
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            print(f"[generate_docs] {action_type.upper()} {file_path}")
            generated_files.append(str(file_path))

        elif action_type == "delete":
            if file_path.exists():
                file_path.unlink()
                print(f"[generate_docs] DELETE {file_path}")
                # Also remove from vector store
                if audience in ("dev", "user"):
                    delete_docs_by_source(audience, str(file_path))
            else:
                print(f"[generate_docs] DELETE skipped: {file_path} does not exist")

        else:
            print(f"[generate_docs] Unknown action: {action_type} for {file_path}")

    # Update vector store with new/modified files
    if generated_files:
        print("[generate_docs] Updating vector store...")
        update_index_after_generation(generated_files)

    print("[generate_docs] Pipeline completed successfully.")


if __name__ == "__main__":
    main()
