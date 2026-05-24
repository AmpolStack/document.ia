"""LLM client: call DeepSeek and parse JSON response."""

import json
import re
import logging
from typing import Any, Dict, List

from llama_index.core import Settings

logger = logging.getLogger(__name__)


def call_llm(prompt: str) -> str:
    """Send prompt to the configured LLM and return the raw response."""
    response = Settings.llm.complete(prompt)
    return response.text


def _clean_json_text(text: str) -> str:
    result = []
    i = 0
    while i < len(text):
        if text[i] != '\\':
            result.append(text[i])
            i += 1
            continue
        if i + 1 >= len(text):
            result.append(text[i])
            i += 1
            continue
        nxt = text[i + 1]
        if nxt in {'"', '\\', '/', 'b', 'f', 'n', 'r', 't', 'u'}:
            result.append(text[i])
            result.append(nxt)
            i += 2
        elif nxt in {'\n', '\r'}:
            i += 2
            if nxt == '\r' and i < len(text) and text[i] == '\n':
                i += 1
        else:
            result.append(nxt)
            i += 2
    return ''.join(result)


def parse_llm_response(raw: str) -> List[Dict[str, Any]]:
    """Extract and parse the JSON actions block from an LLM response.

    Strips invalid JSON escapes that the LLM often generates
    (markdown escaping like \\_, \\-, line continuations, etc.).
    """
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in LLM response")
    text = _clean_json_text(match.group(0))
    data = json.loads(text)
    return data.get("actions", [])


def decide_actions(prompt: str) -> List[Dict[str, Any]]:
    """Send prompt, parse response, and return the list of actions."""
    logger.info("Sending prompt to LLM...")
    raw = call_llm(prompt)
    logger.info(f"Raw LLM response: {raw[:500]}...")
    actions = parse_llm_response(raw)
    logger.info(f"{len(actions)} actions decided.")
    return actions
