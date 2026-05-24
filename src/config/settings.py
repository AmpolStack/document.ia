"""Project-wide settings organized by consuming module.

Each section corresponds to a specific module that owns that configuration.
Import only what you need rather than pulling in the entire module.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

ROOT = Path.cwd()

# docs/schema.py 
SCHEMA_PATH = ROOT / "docs" / "schema.yml"

# git diff settings 
DEFAULT_GIT_BASE_REF = "HEAD~1"
DIFF_MAX_LINES_PER_FILE = 280

# chunk settings
CHUNK_SIZE = 300
CHUNK_OVERLAP = 30

# rag settings
VECTOR_STORE_PATH = str(ROOT / "vector_store")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_BATCH_SIZE = 10
PIPELINE_STATE_PATH = ROOT / ".doc_pipeline_state.json"
RAG_TOP_K = 3
RAG_SCORE_THRESHOLD = 0.15

# llm client settings
LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLM_BASE_URL = "https://api.deepseek.com"
LLM_MODEL = "deepseek-v4-flash"
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "10000"))

DOCS_ROOT = ROOT / "docs"
DOC_EXISTING_SIMILARITY_THRESHOLD = 0.72