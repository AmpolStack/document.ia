from __future__ import annotations

import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

from src.diff_parser import FileChange, format_diff_for_prompt, get_structured_diff

load_dotenv()

ROOT = Path.cwd()
SCHEMA_PATH = ROOT / "docs" / "schema.yml"
DEV_DOC_PATH = ROOT / "docs" / "dev"
USER_DOC_PATH = ROOT / "docs" / "user"


def load_schema() -> dict:
    print(f"[generate_docs] Loading schema from {SCHEMA_PATH}")

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(SCHEMA_PATH)

    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
        schema = yaml.safe_load(f)

    print("[generate_docs] Schema loaded.")
    return schema


def get_docs_tree(base_path: Path, label: str) -> dict[str, str]:
    print(f"[generate_docs] Reading {label} docs from {base_path}")

    if not base_path.exists():
        print(f"[generate_docs] {base_path} does not exist.")
        return {}

    tree: dict[str, str] = {}
    for path in base_path.rglob("*.md"):
        content = path.read_text(encoding="utf-8")
        tree[str(path)] = content

    print(f"[generate_docs] {len(tree)} markdown file(s) found in {label}")
    return tree


def main() -> None:
    print("test 3\n")
    print("[generate_docs] Starting read-only pipeline")
    schema = load_schema()

    changes: list[FileChange] = get_structured_diff()
    if not changes:
        print("[generate_docs] No changes in src/. Exiting.")
        sys.exit(0)

    diff_text = format_diff_for_prompt(changes)
    dev_tree = get_docs_tree(DEV_DOC_PATH, label="developer")
    user_tree = get_docs_tree(USER_DOC_PATH, label="user")

    print("[generate_docs] Summary")
    print(f"  modified src files: {len(changes)}")
    for c in changes:
        print(f"    - {c.change_summary}")
    print(f"  developer docs: {len(dev_tree)}")
    print(f"  user docs: {len(user_tree)}")
    print(f"  formatted diff chars: {len(diff_text)}")


if __name__ == "__main__":
    main()
