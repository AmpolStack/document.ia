from __future__ import annotations

import re
import subprocess
from pathlib import Path

from src.config import FileChange

REPO_ROOT = Path.cwd()


def get_structured_diff(
    base_ref: str = "HEAD~1",
    target_ref: str = "HEAD",
    path: str = "src/"
) -> list[FileChange]:
    diff_path = str(Path(path))
    print(f"[diff_parser] git diff {base_ref}..{target_ref} -- {diff_path}")

    result = subprocess.run(
        ["git", "diff", base_ref, target_ref, "--unified=5", "--", diff_path],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    if result.returncode != 0:
        print("[diff_parser] Error running git diff.")
        raise RuntimeError(result.stderr or "git diff failed")

    raw = result.stdout
    if not raw.strip():
        print("[diff_parser] No changes found.")
        return []

    print(f"[diff_parser] Raw diff lines: {len(raw.splitlines())}")
    print("[diff_parser] Raw diff:")
    print(raw)
    print("[diff_parser] End raw diff")

    changes = _parse_diff(raw)
    print(f"[diff_parser] Parsed {len(changes)} changed file(s)")
    return changes


def _parse_diff(raw: str) -> list[FileChange]:
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


def format_diff_for_prompt(changes: list[FileChange], max_lines_per_file: int = 80) -> str:
    parts: list[str] = []
    for change in changes:
        hunk_text = "\n".join(change.hunks[:max_lines_per_file])
        parts.append(
            """### Archivo: `{}`
Resumen: {}
```diff
{}
```""".format(change.filename, change.change_summary, hunk_text)
        )

    formatted = "\n\n".join(parts)
    print(f"[diff_parser] Diff formatted for prompt ({len(formatted)} chars)")
    return formatted


if __name__ == "__main__":
    print("=== TEST diff_parser.py ===\n")
    changes = get_structured_diff()

    if not changes:
        print("Sin cambios. Asegúrate de tener al menos 2 commits con cambios en src/")
    else:
        print(f"\n=== RESUMEN: {len(changes)} archivo(s) modificado(s) ===")
        for c in changes:
            print(f"  - {c.change_summary}")

