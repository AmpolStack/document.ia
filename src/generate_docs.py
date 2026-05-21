"""Main orchestration entry point for automatic documentation generation.

This module coordinates the full project workflow:
1. Resolve the commit range that still needs documentation.
2. Extract source-code changes from ``src/``.
3. Read and inventory existing markdown documentation.
4. Retrieve relevant semantic context from the vector store.
5. Ask the LLM which documentation actions should occur.
6. Harden those actions against obviously redundant outcomes.
7. Persist markdown updates and refresh the vector store.
8. Maintain static-site index pages under ``docs/``.

Project implications:
- This file is the operational heart of the project. Most "why did the bot
  document this?" questions trace back to choices made here.
- The module intentionally mixes deterministic checks with LLM-driven judgment
  so the system remains flexible without becoming completely unconstrained.
- Changes here affect cost, duplication behavior, CI safety, and the developer
  review experience on the dedicated documentation branch.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
import re
from difflib import SequenceMatcher
from dotenv import load_dotenv

import yaml

from src.config import (
    SCHEMA_PATH,
    DEV_DOC_PATH,
    USER_DOC_PATH,
    PIPELINE_STATE_PATH,
    DOC_EXISTING_SIMILARITY_THRESHOLD,
)
from src.diff_parser import (
    FileChange,
    format_diff_for_prompt,
    get_current_head,
    get_structured_diff,
    resolve_diff_base,
)
from src.llm_decider import decide_actions
from src.docs_site_sync import sync_docs_site_indexes
from src.rag_manager import (
    query_relevant_context,
    is_collection_empty,
    index_directory,
    update_index_after_generation,
    delete_docs_by_source,
)

# Add the repository root so direct module execution behaves consistently in
# local shells and CI environments.
sys.path.append(str(Path(__file__).resolve().parent.parent))
load_dotenv()


def load_schema() -> dict:
    """Load and parse the project documentation schema.

    Returns:
        Parsed schema configuration.

    Raises:
        FileNotFoundError: If ``schema.yml`` does not exist.

    Project implications:
    - The schema acts as the policy layer of the project. If it changes, the
      same code diff can lead to different documentation outcomes.
    """
    print(f"[generate_docs] Loading schema from {SCHEMA_PATH}")

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        schema = yaml.safe_load(f)

    print("[generate_docs] Schema loaded successfully.")
    return schema


def load_pipeline_state() -> dict:
    """Load persisted pipeline state from disk.

    The state currently stores the last processed commit so the pipeline can
    avoid re-documenting the same revision across executions.
    """
    if not PIPELINE_STATE_PATH.exists():
        return {}
    try:
        return json.loads(PIPELINE_STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("[generate_docs] Warning: pipeline state is invalid JSON. Resetting state.")
        return {}


def save_pipeline_state(state: dict) -> None:
    """Persist pipeline state to disk for future runs."""
    PIPELINE_STATE_PATH.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def ensure_schema() -> None:
    """Ensure ``schema.yml`` exists, creating a minimal fallback if required.

    Project implications:
    - The generated fallback schema keeps the pipeline runnable, but it is only
      a safety net. Real project behavior should be driven by the curated
      schema checked into ``docs/``.
    """
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
    """Read every markdown file under a documentation root.

    Args:
        base_path: Root directory containing markdown documentation.
        label: Human-readable audience label used in logs.

    Returns:
        Mapping from absolute file path to file content.

    Project implications:
    - This direct filesystem view complements the vector store and provides a
      deterministic source of truth about what docs currently exist.
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


def build_docs_inventory(tree: dict[str, str]) -> str:
    """Build a compact inventory of existing docs for the LLM.

    The inventory gives the model explicit visibility into which files already
    exist, which helps reduce duplicate ``create`` actions.
    """
    if not tree:
        return ""

    lines: list[str] = []
    for raw_path, content in sorted(tree.items()):
        path = Path(raw_path)
        relative = path.relative_to(Path.cwd()).as_posix()
        heading = ""
        for line in content.splitlines():
            if line.startswith("# "):
                heading = line[2:].strip()
                break
        summary = heading or path.stem.replace("-", " ").replace("_", " ")
        lines.append(f"- {relative} | {summary}")
    return "\n".join(lines)


def normalize_doc_key(value: str) -> str:
    """Normalize a path or title into a comparison-friendly concept slug."""
    text = Path(value).stem.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def find_similar_existing_doc(raw_file_path: str, audience_root: Path) -> Path | None:
    """Find an existing docs file with a similar conceptual slug.

    This deterministic check is used to catch obviously redundant creations
    before file writes happen.
    """
    target_key = normalize_doc_key(raw_file_path)
    best_match: Path | None = None
    best_score = 0.0

    for existing in audience_root.rglob("*.md"):
        if existing.name.lower() in {"index.md", "readme.md"}:
            continue
        existing_key = normalize_doc_key(existing.name)
        score = SequenceMatcher(None, target_key, existing_key).ratio()
        if target_key == existing_key:
            return existing
        if score > best_score:
            best_score = score
            best_match = existing

    if best_match and best_score >= DOC_EXISTING_SIMILARITY_THRESHOLD:
        return best_match
    return None


def harden_actions_against_existing_docs(actions: list[dict[str, str]]) -> list[dict[str, str]]:
    """Reduce redundant ``create`` actions using filesystem evidence.

    Project implications:
    - This function represents the project's preference for constrained LLM
      automation: let the model reason, but verify easy duplication cases with
      deterministic checks.
    """
    hardened: list[dict[str, str]] = []

    for action in actions:
        action_type = action.get("type")
        audience = action.get("audience")
        raw_file_path = action.get("file", "")

        if action_type != "create" or audience not in {"dev", "user"}:
            hardened.append(action)
            continue

        audience_root = DEV_DOC_PATH if audience == "dev" else USER_DOC_PATH
        similar_doc = find_similar_existing_doc(raw_file_path, audience_root)

        if similar_doc is None:
            hardened.append(action)
            continue

        updated_action = dict(action)
        updated_action["type"] = "update"
        updated_action["file"] = similar_doc.relative_to(Path.cwd()).as_posix()
        print(
            "[generate_docs] Hardened redundant CREATE into UPDATE "
            f"for existing doc: {updated_action['file']}"
        )
        hardened.append(updated_action)

    return hardened


def resolve_safe_docs_path(raw_path: str | None) -> Path | None:
    """Resolve an LLM-provided path and ensure it stays inside ``docs/``.

    The model is allowed to propose new documentation files, but never outside
    the project documentation tree. This function is the security boundary for
    that rule.
    """
    if not raw_path:
        return None

    candidate = Path(raw_path)
    docs_root = (Path.cwd() / "docs").resolve()

    if candidate.is_absolute():
        resolved_path = candidate.resolve()
    else:
        resolved_path = (Path.cwd() / candidate).resolve()

    try:
        resolved_path.relative_to(docs_root)
    except ValueError:
        return None

    return resolved_path


def main() -> None:
    """Execute the full documentation generation pipeline.

    This function:
    1. Ensures schema availability.
    2. Loads persisted state and resolves the correct git diff base.
    3. Detects relevant source-code changes.
    4. Reads existing docs and retrieves semantic context.
    5. Calls the LLM to decide documentation actions.
    6. Applies deterministic hardening against redundant work.
    7. Writes documentation changes to disk.
    8. Refreshes the vector store and site-navigation indexes.

    Project implications:
    - This entry point is designed to be CI-safe, re-runnable, and conservative
      about redundant documentation work.
    - Persisted commit state makes the pipeline commit-aware rather than merely
      workspace-aware, which is crucial for GitHub Actions.
    """
    print("[generate_docs] Starting automatic documentation pipeline")

    # Ensure schema exists
    ensure_schema()

    pipeline_state = load_pipeline_state()
    current_head = get_current_head()
    last_processed_commit = pipeline_state.get("last_processed_commit")
    diff_base = resolve_diff_base(last_processed_commit)

    if diff_base is None:
        updated_index_files = sync_docs_site_indexes()
        if updated_index_files:
            print("[generate_docs] Updating vector store for synced indexes...")
            update_index_after_generation([str(path) for path in updated_index_files])
        print("[generate_docs] Current HEAD was already processed. Exiting.")
        sys.exit(0)

    # Get code changes
    changes = get_structured_diff(base_ref=diff_base, target_ref=current_head)
    if not changes:
        updated_index_files = sync_docs_site_indexes()
        if updated_index_files:
            print("[generate_docs] Updating vector store for synced indexes...")
            update_index_after_generation([str(path) for path in updated_index_files])
        print("[generate_docs] No changes detected in src/. Exiting.")
        sys.exit(0)

    # Index existing documentation if first time
    if is_collection_empty("dev"):
        print("[generate_docs] Indexing developer documentation...")
        index_directory("dev", str(DEV_DOC_PATH))
    if is_collection_empty("user"):
        print("[generate_docs] Indexing user documentation...")
        index_directory("user", str(USER_DOC_PATH))

    dev_tree = get_docs_tree(DEV_DOC_PATH, "developer")
    user_tree = get_docs_tree(USER_DOC_PATH, "user")
    dev_docs_inventory = build_docs_inventory(dev_tree)
    user_docs_inventory = build_docs_inventory(user_tree)

    # Prepare diff and context
    diff_text = format_diff_for_prompt(changes)
    dev_context = query_relevant_context(diff_text, audience="dev")
    user_context = query_relevant_context(diff_text, audience="user")

    print("[generate_docs] Summary:")
    print(f"  - Files modified: {len(changes)}")
    print(f"  - Dev context: {len(dev_context)} characters")
    print(f"  - User context: {len(user_context)} characters")

    print("[generate_docs] Debug: Prompt sent to LLM:")
    print(diff_text)
    print("[generate_docs] Debug: Developer context:")
    print(dev_context)
    print("[generate_docs] Debug: User context:")
    print(user_context)

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

    actions = harden_actions_against_existing_docs(actions)

    if not actions:
        print("[generate_docs] LLM determined no documentation changes are required.")
        sys.exit(0)

    # Execute actions
    generated_files = []
    for action in actions:
        action_type = action.get("type")
        audience = action.get("audience")
        raw_file_path = action.get("file")
        file_path = resolve_safe_docs_path(raw_file_path)
        content = action.get("content", "")

        # Validate path is within docs/ (security check)
        if file_path is None:
            print(f"[generate_docs] Unsafe path ignored: {raw_file_path}")
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
    index_files_for_reindex: list[str] = []

    if generated_files:
        print("[generate_docs] Updating vector store...")
        update_index_after_generation(generated_files)

    print("[generate_docs] Syncing docs site indexes...")
    updated_index_files = sync_docs_site_indexes()
    index_files_for_reindex = [str(path) for path in updated_index_files]

    if index_files_for_reindex:
        print("[generate_docs] Updating vector store for synced indexes...")
        update_index_after_generation(index_files_for_reindex)

    pipeline_state["last_processed_commit"] = current_head
    save_pipeline_state(pipeline_state)
    print(f"[generate_docs] Recorded processed HEAD: {current_head}")

    print("[generate_docs] Pipeline completed successfully.")


if __name__ == "__main__":
    main()
