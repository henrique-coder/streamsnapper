# Standard modules
from sys import stderr

# Third-party modules
from loguru import logger


# Configure logger
logger.remove()
logger.add(
    stderr,
    level="DEBUG",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}</cyan> | <level>{message}</level>",
    colorize=True,
)
