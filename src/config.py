"""Central configuration for the automated documentation pipeline.

This module defines the shared configuration used across local runs and GitHub
Actions executions. It centralizes filesystem paths, LLM behavior, retrieval
thresholds, diff sizing, and deduplication heuristics so the project does not
depend on scattered hardcoded values.

Project implications:
- Configuration changes here can alter documentation cost, precision, and
  duplication behavior without changing the rest of the code.
- Centralizing these values improves reviewability and makes CI behavior easier
  to reason about.
- The project treats these constants as part of its policy surface, especially
  for retrieval aggressiveness and prompt sizing.
"""

from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables early so imported modules can safely consume
# secrets and runtime settings without relying on call order.
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
    """Structured representation of a source-code diff for one file.

    Attributes:
        filename: Repository-relative path to the changed file.
        added_lines: Added code lines with diff markers removed.
        removed_lines: Removed code lines with diff markers removed.
        hunks: Raw diff hunk lines preserved for prompt construction.
        change_summary: Human-readable summary used in logs and prompts.

    Project implications:
    - This object is the boundary between raw git history and LLM-facing
      reasoning.
    - Preserving both normalized line lists and raw hunks gives the pipeline
      room to evolve toward stronger deterministic validation later.
    """

    filename: str
    added_lines: list[str]
    removed_lines: list[str]
    hunks: list[str]
    change_summary: str
