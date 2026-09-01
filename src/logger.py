# src/logger.py

import logging
import sys
from pathlib import Path


# =========================================================
# 日志目录
# =========================================================

LOG_DIR = Path("logs")

LOG_DIR.mkdir(
    exist_ok=True
)


# =========================================================
# 日志文件
# =========================================================

LOG_FILE = (
    LOG_DIR
    / "app.log"
)


# =========================================================
# Logger
# =========================================================

logger = logging.getLogger(
    "AI-News-Agent"
)


logger.setLevel(
    logging.INFO
)


# =========================================================
# 防止重复添加 Handler
# =========================================================

if not logger.handlers:

    # -----------------------------------------------------
    # 日志格式
    # -----------------------------------------------------

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )


    # -----------------------------------------------------
    # 文件 Handler
    # -----------------------------------------------------

    file_handler = logging.FileHandler(

        LOG_FILE,

        encoding="utf-8"

    )


    file_handler.setFormatter(
        formatter
    )


    # -----------------------------------------------------
    # 控制台 Handler
    #
    # 关键修改：
    # 明确使用 stdout
    # -----------------------------------------------------

    console_handler = logging.StreamHandler(
        sys.stdout
    )


    console_handler.setFormatter(
        formatter
    )


    # -----------------------------------------------------
    # 添加 Handler
    # -----------------------------------------------------

    logger.addHandler(
        file_handler
    )


    logger.addHandler(
        console_handler
    )