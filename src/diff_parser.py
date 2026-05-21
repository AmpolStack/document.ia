"""Git diff extraction and normalization for documentation decisions.

This module converts repository history into a prompt-friendly representation
that the rest of the pipeline can reason about. It focuses on ``src/`` because
the project treats source-code changes as the trigger for documentation
updates.

Project implications:
- The selected commit range defines what the bot believes is "new work".
- The shape and size of the generated diff strongly influence LLM quality.
- Because this layer is text-based and language-agnostic, it is simple and
  robust, but it cannot infer semantics beyond what the diff exposes.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Optional

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

    Project implications:
    - This function defines the exact change slice the documentation system
      sees.
    - If the base ref is wrong, the project can re-document old commits or
      miss documentation for new ones.
    """
    diff_path = str(Path(path))
    print(f"[diff_parser] Running git diff {base_ref}..{target_ref} -- {diff_path}")

    result = subprocess.run(
        ["git", "diff", base_ref, target_ref, "--unified=5", "--", diff_path],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    if result.returncode != 0:
        print("[diff_parser] Error running git diff command.")
        raise RuntimeError(result.stderr or "git diff failed")

    raw = result.stdout
    if not raw.strip():
        print("[diff_parser] No changes detected.")
        return []

    print(f"[diff_parser] Raw diff lines: {len(raw.splitlines())}")
    print("[diff_parser] Raw diff output:")
    print(raw)
    print("[diff_parser] End raw diff output")

    changes = _parse_diff(raw)
    print(f"[diff_parser] Parsed {len(changes)} changed file(s)")
    return changes


def get_current_head() -> str:
    """Return the current repository ``HEAD`` commit hash.

    Project implications:
    - The pipeline stores this value to avoid reprocessing the same commit on
      subsequent runs.
    """
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

    Project implications:
    - This is a key safeguard against redundant documentation generation.
    - If the persisted state becomes stale or corrupted, the project may skip
      necessary work or re-run historical work.
    """
    current_head = get_current_head()
    if last_processed_commit and last_processed_commit == current_head:
        print(f"[diff_parser] HEAD {current_head} was already processed.")
        return None
    if last_processed_commit:
        return last_processed_commit
    return DEFAULT_GIT_BASE_REF


def _parse_diff(raw: str) -> list[FileChange]:
    """Parse raw ``git diff`` output into ``FileChange`` records.

    Args:
        raw: Exact stdout emitted by the git diff command.

    Returns:
        List of parsed ``FileChange`` objects.
    """
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
    """Create a normalized ``FileChange`` object from raw diff fragments.

    Args:
        filename: Repository-relative filename from the diff header.
        added: Added lines stripped of their leading diff marker.
        removed: Removed lines stripped of their leading diff marker.
        hunks: Raw diff lines preserved in order.

    Returns:
        A populated ``FileChange`` value ready for prompt formatting.
    """
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

    print(f"[diff_parser] Parsed file change: {change.change_summary}")
    if added:
        print(f"              Added ({len(added)}): {added[:5]}{'...' if len(added) > 5 else ''}")
    if removed:
        print(f"              Removed ({len(removed)}): {removed[:5]}{'...' if len(removed) > 5 else ''}")
    return change


def format_diff_for_prompt(
    changes: list[FileChange],
    max_lines_per_file: int = DIFF_MAX_LINES_PER_FILE,
) -> str:
    """Render parsed file changes into a compact markdown diff prompt.

    Args:
        changes: Structured file changes to serialize.
        max_lines_per_file: Maximum number of raw diff lines retained per file.

    Returns:
        Prompt-friendly markdown string.

    Project implications:
    - This is the last deterministic step before LLM reasoning.
    - The line budget is a direct trade-off between completeness and token
      efficiency, which affects whether the model can recognize existing docs
      coverage.
    """
    parts: list[str] = []
    for change in changes:
        hunk_text = "\n".join(change.hunks[:max_lines_per_file])
        formatted_part = f"### File: `{change.filename}`\nSummary: {change.change_summary}\n```diff\n{hunk_text}\n```"
        parts.append(formatted_part)

    formatted = "\n\n".join(parts)
    print(f"[diff_parser] Diff formatted for prompt ({len(formatted)} characters)")
    return formatted


if __name__ == "__main__":
    print("=== Testing diff_parser.py ===\n")
    changes = get_structured_diff()

    if not changes:
        print("No changes detected. Ensure you have at least 2 commits with changes in src/")
    else:
        print(f"\n=== SUMMARY: {len(changes)} file(s) modified ===")
        for c in changes:
            print(f"  - {c.change_summary}")

