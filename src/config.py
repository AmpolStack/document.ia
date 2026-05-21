"""Configuration module for the documentation pipeline.

This module contains all configuration constants and data structures used
throughout the documentation generation pipeline, including LLM settings,
file paths, and embedding parameters.
"""

from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables FIRST, before any module imports them
load_dotenv()


# ============================================
# PATH CONFIGURATION
# ============================================

ROOT = Path.cwd()
DOCS_ROOT = ROOT / "docs"
SCHEMA_PATH = DOCS_ROOT / "schema.yml"
DEV_DOC_PATH = DOCS_ROOT / "dev"
USER_DOC_PATH = DOCS_ROOT / "user"


# ============================================
# LLM AND EMBEDDING CONFIGURATION
# ============================================

LLM_MODEL = "deepseek-v4-flash"
LLM_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
LLM_BASE_URL = "https://api.deepseek.com"
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 10000

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_BATCH_SIZE = 10

VECTOR_STORE_PATH = str(ROOT / "vector_store")
PIPELINE_STATE_PATH = ROOT / ".doc_pipeline_state.json"

CHUNK_SIZE = 300
CHUNK_OVERLAP = 30
RAG_TOP_K = 3
RAG_SCORE_THRESHOLD = 0.15

DEFAULT_GIT_BASE_REF = "HEAD~1"
DIFF_MAX_LINES_PER_FILE = 280

DOC_EXISTING_SIMILARITY_THRESHOLD = 0.72


@dataclass
class FileChange:
    """Represents a single file change detected in a git diff.

    Attributes:
        filename: Path to the changed file
        added_lines: List of added code lines (without '+' prefix)
        removed_lines: List of removed code lines (without '-' prefix)
        hunks: Raw diff hunks for context preservation
        change_summary: Human-readable summary of the changes
    """

    filename: str
    added_lines: list[str]
    removed_lines: list[str]
    hunks: list[str]
    change_summary: str
