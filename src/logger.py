# src/logger.py

import logging
from pathlib import Path


LOG_DIR = Path("logs")

LOG_DIR.mkdir(
    exist_ok=True
)


LOG_FILE = LOG_DIR / "app.log"


logger = logging.getLogger(
    "AI-News-Agent"
)


logger.setLevel(
    logging.INFO
)


if not logger.handlers:

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )


    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )


    file_handler.setFormatter(
        formatter
    )


    console_handler = logging.StreamHandler()

    console_handler.setFormatter(
        formatter
    )


    logger.addHandler(
        file_handler
    )

    logger.addHandler(
        console_handler
    )