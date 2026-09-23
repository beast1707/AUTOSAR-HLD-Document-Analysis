import logging
import os
import sys

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # File handler
        os.makedirs("./logs", exist_ok=True)
        fh = logging.FileHandler(f"./logs/{name}.log")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
