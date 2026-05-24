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


def parse_llm_response(raw: str) -> List[Dict[str, Any]]:
    """Extract and parse the JSON actions block from an LLM response."""
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in LLM response")
    data = json.loads(match.group(0))
    return data.get("actions", [])


def decide_actions(prompt: str) -> List[Dict[str, Any]]:
    """Send prompt, parse response, and return the list of actions."""
    logger.info("Sending prompt to LLM...")
    raw = call_llm(prompt)
    logger.info(f"Raw LLM response: {raw[:500]}...")
    actions = parse_llm_response(raw)
    logger.info(f"{len(actions)} actions decided.")
    return actions
