from sys import stderr

from loguru import logger


LOG_FORMAT = (
    "<green>{time:HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}:{function}</cyan> | "
    "<level>{message}</level>"
)

# Configure logger
logger.remove()
logger.add(
    stderr,
    level="DEBUG",
    format=LOG_FORMAT,
    colorize=True,
)
