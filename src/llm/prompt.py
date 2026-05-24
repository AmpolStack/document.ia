"""Build the LLM prompt for documentation decision-making."""

from src.config.settings import SCHEMA_PATH
from src.config.models import AUDIENCES
from src.docs.schema import load_schema


EMPTY_ACTIONS = '{"actions": []}'


def build_prompt(diff_text: str, contexts: dict[str, str], inventories: dict[str, str]) -> str:
    """Build the complete LLM prompt.

    Args:
        diff_text: Formatted git diff.
        contexts: Audience label → relevant RAG context.
        inventories: Audience label → compact file inventory.

    Returns:
        Complete prompt string.
    """
    schema = load_schema(SCHEMA_PATH, ensure=True)

    audiences_block = ""
    for a in AUDIENCES:
        ctx = contexts.get(a.label, "Previous context is not available.")
        inv = inventories.get(a.label, "No existing documentation files.")
        audiences_block += f"""
=== AUDIENCE: {a.label} ===
Path: {a.path}
Reason: {a.reason}
Context:
{ctx}

Inventory of existing files:
{inv}
"""

    return f"""You are an assistant that updates technical documentation based on code changes.
The following is provided:
- The **diff** of changes in the source code.
- **Existing documentation context** per audience.
- The **schema** that defines the expected documentation structure.

Your task: Decide which documentation files should be **created, updated, or deleted**
based on the code changes.

Return ONLY a JSON with the following format:

{{
    "actions": [
        {{
            "type": "update",
            "audience": "developer",
            "file": "docs/dev/api-reference.md",
            "content": "complete new markdown content..."
        }},
        {{
            "type": "create",
            "audience": "user",
            "file": "docs/user/faq.md",
            "content": "..."
        }},
        {{
            "type": "delete",
            "audience": "dev",
            "file": "docs/dev/obsolete.md"
        }}
    ]
}}

Rules:
- Only return the JSON, no additional text.
- If no changes are needed, return {EMPTY_ACTIONS}.
- Content must be valid markdown.
- Use the provided context to maintain consistency.
- Prefer `update` over `create` when an existing document already covers the same module, class, function, concept, or user task.
- Prefer returning {EMPTY_ACTIONS} instead of creating redundant documentation when the existing context already covers the detected changes.
- Only use `create` when the required documentation does not already exist in the provided context.
- Never create a duplicate document for a symbol or concept that is already documented; update the existing file instead.
- Before proposing `create`, inspect the inventory of existing files and reuse the closest relevant file whenever possible.
- If an existing file already documents the same source module or concept with a slightly different title, treat it as existing documentation and use `update`.

=== DIFF ===
{diff_text}

{audiences_block}

=== SCHEMA ===
{schema}
"""
