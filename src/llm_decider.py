"""LLM-facing decision layer for documentation planning.

This module turns repository context into an LLM prompt and turns the resulting
response back into structured documentation actions. It does not write files by
itself; instead, it provides the reasoning boundary between deterministic
project inputs and downstream execution.

Project implications:
- Prompt wording here heavily influences whether the system prefers no-op,
  update, or create behavior.
- This is one of the highest-leverage modules in the project: small
  instruction changes can shift documentation outcomes across every CI run.
- Because the project relies on JSON-only responses, prompt clarity and parsing
  robustness directly affect automation reliability.
"""

from __future__ import annotations
import json
import re
from typing import List, Dict, Any
from pathlib import Path

from llama_index.core import Settings
from src.config import SCHEMA_PATH


def load_schema_text() -> str:
    """Load schema.yml file content.

    Returns:
        Content of the schema file as string

    Raises:
        FileNotFoundError: If schema file does not exist
    """
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return f.read()


def build_prompt(
    diff_text: str,
    dev_context: str,
    user_context: str,
    dev_docs_inventory: str,
    user_docs_inventory: str,
) -> str:
    """Build the LLM prompt for documentation decision-making.

    Args:
        diff_text: Formatted git diff text
        dev_context: Relevant developer documentation context
        user_context: Relevant user documentation context
        dev_docs_inventory: Existing developer docs file inventory
        user_docs_inventory: Existing user docs file inventory

    Returns:
        Complete LLM prompt as string
    """
    schema_text = load_schema_text()
    empty_actions = "{\"actions\": []}"
    return f"""You are an assistant that updates technical documentation based on code changes.
The following is provided:
- The **diff** of changes in the source code.
- **Existing documentation context** for developers (dev) and users (user).
- The **schema** that defines the expected documentation structure.

Your task: Decide which documentation files in `docs/dev/` and `docs/user/` should be 
**created, updated, or deleted** based on the code changes.

Return ONLY a JSON with the following format:

{{
    "actions": [
        {{
            "type": "update",
            "audience": "dev",
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
- If no changes are needed, return {empty_actions}.
- Content must be valid markdown.
- Use the provided context to maintain consistency.
- Prefer `update` over `create` when an existing document already covers the same module, class, function, concept, or user task.
- Prefer returning {empty_actions} instead of creating redundant documentation when the existing context already covers the detected changes.
- Only use `create` when the required documentation does not already exist in the provided context.
- Never create a duplicate document for a symbol or concept that is already documented; update the existing file instead.
- Before proposing `create`, inspect the inventory of existing files and reuse the closest relevant file whenever possible.
- If an existing file already documents the same source module or concept with a slightly different title, treat it as existing documentation and use `update`.

=== DIFF ===
{diff_text}

=== DEVELOPER DOCUMENTATION CONTEXT ===
{dev_context if dev_context else "previous context is not available."}

=== EXISTING DEVELOPER DOC FILES ===
{dev_docs_inventory if dev_docs_inventory else "No developer docs files found."}

=== USER DOCUMENTATION CONTEXT ===
{user_context if user_context else "No previous context available."}

=== EXISTING USER DOC FILES ===
{user_docs_inventory if user_docs_inventory else "No user docs files found."}

=== SCHEMA ===
{schema_text}
"""


def call_llm(prompt: str) -> str:
    """Call the configured LLM and return the response.

    Args:
        prompt: The prompt to send to the LLM

    Returns:
        LLM response text

    Raises:
        Exception: If LLM call fails
    """
    response = Settings.llm.complete(prompt)
    return response.text


def parse_llm_response(raw: str) -> List[Dict[str, Any]]:
    """Extract and parse JSON from LLM response.

    Args:
        raw: Raw LLM response text

    Returns:
        List of action dictionaries extracted from JSON response

    Raises:
        ValueError: If no valid JSON found in response
        json.JSONDecodeError: If JSON parsing fails
    """
    # Search for JSON block with braces
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in LLM response")
    json_str = match.group(0)
    data = json.loads(json_str)
    return data.get("actions", [])


def decide_actions(
    diff_text: str,
    dev_context: str,
    user_context: str,
    dev_docs_inventory: str,
    user_docs_inventory: str,
) -> List[Dict[str, Any]]:
    """Orchestrate the LLM call and return the list of actions to execute.

    Args:
        diff_text: Formatted git diff text
        dev_context: Relevant developer documentation context
        user_context: Relevant user documentation context
        dev_docs_inventory: Existing developer docs file inventory
        user_docs_inventory: Existing user docs file inventory

    Returns:
        List of action dictionaries to execute

    Raises:
        Exception: If LLM call or parsing fails
    """
    prompt = build_prompt(
        diff_text,
        dev_context,
        user_context,
        dev_docs_inventory,
        user_docs_inventory,
    )
    print("[llm_decider] Sending prompt to LLM...")
    raw_response = call_llm(prompt)
    print("[llm_decider] Raw LLM response:")
    print(f"[llm_decider_resp]: {raw_response}")
    print("[llm_decider] Response received, parsing...")
    actions = parse_llm_response(raw_response)
    print(f"[llm_decider] {len(actions)} actions decided.")
    return actions
