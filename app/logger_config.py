import logging

logger = logging.getLogger("taskmaster")
logger.setLevel(logging.ERROR)

if not logger.handlers:
    file_handler = logging.FileHandler("app.log")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

logger.propagate = False
