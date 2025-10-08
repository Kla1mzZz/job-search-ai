import logging
from logging.handlers import RotatingFileHandler
import sys


logger = logging.getLogger("llm_service")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# file_handler = RotatingFileHandler(
#     "logs/similarity_service.log", maxBytes=5 * 1024 * 1024, backupCount=5
# )
# file_handler.setLevel(logging.DEBUG)
# file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
# logger.addHandler(file_handler)
