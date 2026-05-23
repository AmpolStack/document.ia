from dotenv import load_dotenv
import yaml
import logging
from src.config import SCHEMA_PATH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    # datefmt="%Y-%m-%d %H:%M:%S"
)

load_dotenv()
logger = logging.getLogger(__name__)

DEFAULT_SCHEMA = {
    "version": "1.0",
    "documentation": {
        "dev": {
            "description": "Developer-focused documentation",
            "sections": ["API Reference", "Architecture", "Setup", "Contributing"]
        },
        "user": {
            "description": "User-focused documentation",
            "sections": ["Getting Started", "User Guide", "FAQ", "Troubleshooting"]
        }
    }
}

def load_schema(ensure=False) -> dict:
    """Load and parse the documentation schema.

    Returns:
        Dictionary containing the schema definition

    Raises:
        FileNotFoundError: If schema.yml does not exist
    """
    logger.info(f"Loading schema from {SCHEMA_PATH}")

    if not SCHEMA_PATH.exists():
        if ensure:
            logger.warning("Schema file not found. Creating default schema...")
            _ensure_schema()
            with SCHEMA_PATH.open("r", encoding="utf-8") as f:
                schema = yaml.safe_load(f)
        else:
            raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")
  
    with SCHEMA_PATH.open("r", encoding="utf-8") as f:
            schema = yaml.safe_load(f)
    logger.info("Schema loaded successfully.")
    return schema


def _ensure_schema() -> None:
    """Creating a default one if necessary."""
    SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)

    with SCHEMA_PATH.open("w", encoding="utf-8") as f:
        yaml.dump(DEFAULT_SCHEMA, f, default_flow_style=False)

    logger.info(f"Default schema created at {SCHEMA_PATH}")


if __name__ == "__main__":
    try:
        content = load_schema(ensure=True)
        logger.info(f"Content: {content}")
    except FileNotFoundError as e:
        logger.error(str(e))