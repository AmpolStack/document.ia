"""Git diff extraction and normalization for documentation decisions.

This module converts repository history into a prompt-friendly representation
that the rest of the pipeline can reason about. It focuses on ``src/`` because
the project treats source-code changes as the trigger for documentation
updates.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

from src.config import DEFAULT_GIT_BASE_REF, DIFF_MAX_LINES_PER_FILE, FileChange

REPO_ROOT = Path.cwd()


def get_structured_diff(
    base_ref: str = DEFAULT_GIT_BASE_REF,
    target_ref: str = "HEAD",
    path: str = "src/"
) -> list[FileChange]:
    """Extract structured source-code changes between two git references.

    Args:
        base_ref: Git reference used as the comparison baseline.
        target_ref: Git reference treated as the new state.
        path: Repository subpath to analyze, usually ``src/``.

    Returns:
        List of FileChange objects representing modified files

    Raises:
        RuntimeError: If the git command fails.
    """
    diff_path = str(Path(path))
    logger.info(f"Running git diff {base_ref}..{target_ref} -- {diff_path}")

    result = subprocess.run(
        ["git", "diff", base_ref, target_ref, "--unified=5", "--", diff_path],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    if result.returncode != 0:
        logger.error("Error running git diff command.")
        raise RuntimeError(result.stderr or "git diff failed")

    raw = result.stdout
    if not raw.strip():
        logger.info("No changes detected.")
        return []

    logger.info(f"Raw diff lines: {len(raw.splitlines())}")
    logger.info("Raw diff output:")
    logger.info(raw)
    logger.info("End raw diff output")

    changes = _parse_diff(raw)
    logger.info(f"Parsed {len(changes)} changed file(s)")
    return changes


def get_current_head() -> str:
    """Return the current repository ``HEAD`` commit hash."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or "git rev-parse HEAD failed")
    return result.stdout.strip()


def resolve_diff_base(last_processed_commit: Optional[str]) -> Optional[str]:
    """Resolve the appropriate git base for the next documentation run.

    Returns ``None`` when the current ``HEAD`` was already processed.
    """
    current_head = get_current_head()
    if last_processed_commit and last_processed_commit == current_head:
        logger.info(f"HEAD {current_head} was already processed.")
        return None
    if last_processed_commit:
        return last_processed_commit
    return DEFAULT_GIT_BASE_REF


def _parse_diff(raw: str) -> list[FileChange]:
    """Parse raw ``git diff`` output into ``FileChange`` records."""
    changes: list[FileChange] = []
    current_file = None
    current_hunks: list[str] = []
    added: list[str] = []
    removed: list[str] = []

    for line in raw.splitlines():
        if line.startswith("diff --git"):
            if current_file:
                changes.append(_build_change(current_file, added, removed, current_hunks))
            match = re.search(r"b/(.+)$", line)
            current_file = match.group(1) if match else "unknown"
            current_hunks, added, removed = [], [], []

        elif line.startswith("@@"):
            current_hunks.append(line)

        elif line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:])
            current_hunks.append(line)

        elif line.startswith("-") and not line.startswith("---"):
            removed.append(line[1:])
            current_hunks.append(line)

        else:
            current_hunks.append(line)

    if current_file:
        changes.append(_build_change(current_file, added, removed, current_hunks))

    return changes


def _build_change(
    filename: str,
    added: list[str],
    removed: list[str],
    hunks: list[str],
) -> FileChange:
    """Create a normalized ``FileChange`` object from raw diff fragments."""
    parts: list[str] = []
    if added:
        parts.append(f"{len(added)} added")
    if removed:
        parts.append(f"{len(removed)} removed")

    change = FileChange(
        filename=filename,
        added_lines=added,
        removed_lines=removed,
        hunks=hunks,
        change_summary=f"{filename}: {', '.join(parts) or 'no net changes'}",
    )

    logger.info(f"Parsed file change: {change.change_summary}")
    if added:
        logger.info(f"              Added ({len(added)}): {added[:5]}{'...' if len(added) > 5 else ''}")
    if removed:
        logger.info(f"              Removed ({len(removed)}): {removed[:5]}{'...' if len(removed) > 5 else ''}")
    return change


def format_diff_for_prompt(
    changes: list[FileChange],
    max_lines_per_file: int = DIFF_MAX_LINES_PER_FILE,
) -> str:
    """Render parsed file changes into a compact markdown diff prompt.

    Args:
        changes: Structured file changes to serialize.
        max_lines_per_file: Maximum number of raw diff lines retained per file.
    """
    parts: list[str] = []
    for change in changes:
        hunk_text = "\n".join(change.hunks[:max_lines_per_file])
        formatted_part = f"### File: `{change.filename}`\nSummary: {change.change_summary}\n```diff\n{hunk_text}\n```"
        parts.append(formatted_part)

    formatted = "\n\n".join(parts)
    logger.info(f"Diff formatted for prompt ({len(formatted)} characters)")
    return formatted


if __name__ == "__main__":
    logger.info("=== Testing diff_parser.py ===")
    changes = get_structured_diff()

    if not changes:
        logger.info("No changes detected. Ensure you have at least 2 commits with changes in src/")
    else:
        logger.info(f"\n=== SUMMARY: {len(changes)} file(s) modified ===")
        for c in changes:
            logger.info(f"  - {c.change_summary}")
