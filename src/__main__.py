"""Entry point: ``python -m src``"""

import sys
from src._logging import configure_logging
from src.pipeline.orchestrator import run


def main() -> None:
    configure_logging()
    try:
        run()
    except Exception:
        import logging
        logging.exception("Pipeline failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
