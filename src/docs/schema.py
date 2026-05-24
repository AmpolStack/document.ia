"""Load and manage the documentation schema (schema.yml)."""

from pathlib import Path

import yaml
import logging

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

def load_schema(path: Path, ensure: bool = False) -> dict:
    """Load and parse the documentation schema.

    Args:
        path: Path to the schema.yml file.
        ensure: If True, create a default schema when the file is missing.

    Returns:
        Dictionary containing the schema definition.

    Raises:
        FileNotFoundError: If schema.yml does not exist and ensure is False.
    """
    logger.info(f"Loading schema from {path}")

    if not path.exists():
        if ensure:
            logger.warning("Schema file not found. Creating default schema...")
            _ensure_schema(path)
        else:
            raise FileNotFoundError(f"Schema file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        schema = yaml.safe_load(f)
    logger.info("Schema loaded successfully.")
    return schema


def _ensure_schema(path: Path) -> None:
    """Create a default schema file if it doesn't exist."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.dump(DEFAULT_SCHEMA, f, default_flow_style=False)
    logger.info(f"Default schema created at {path}")


if __name__ == "__main__":
    try:
        content = load_schema(Path("../../docs/schema.yml"), ensure=True)
        print(content)
        logger.info(f"Content: {content}")
    except FileNotFoundError as e:
        logger.error(str(e))
