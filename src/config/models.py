"""Data models (dataclasses) used across the pipeline."""

from dataclasses import dataclass


@dataclass
class FileChange:
    """Structured representation of a source-code diff for one file.

    Attributes:
        filename: Repository-relative path to the changed file.
        added_lines: Added code lines with diff markers removed.
        removed_lines: Removed code lines with diff markers removed.
        hunks: Raw diff hunk lines preserved for prompt construction.
        change_summary: Human-readable summary used in logs and prompts.
    """

    filename: str
    added_lines: list[str]
    removed_lines: list[str]
    hunks: list[str]
    change_summary: str


@dataclass
class DocAction:
    """Action decided by the LLM to apply on the documentation tree."""

    type: str       # "create" | "update" | "delete"
    audience: str   # audience label (e.g. "developer", "user")
    file: str       # relative path under docs/
    content: str = ""


@dataclass
class Audience:
    """Documentation audience configuration.

    Attributes:
        path: Directory path for this audience's documentation.
        label: Unique identifier used as ChromaDB collection name.
        similarity_threshold: Minimum similarity to consider a doc match.
    """
    path: str
    label: str
    similarity_threshold: float = 0.72
    reason: str = ""


# ── pipeline/orchestrator.py ──
AUDIENCES: list[Audience] = [
    Audience(
        path="docs/dev",
        label="developer",
        similarity_threshold=0.72,
        reason="Use for code-level documentation: APIs, classes, functions, architecture, internal modules, and technical setup.",
    ),
    Audience(
        path="docs/user",
        label="user",
        similarity_threshold=0.72,
        reason="Use for end-user facing documentation: tutorials, how-to guides, FAQs, and product explanations.",
    ),
]