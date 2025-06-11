"""Logger configuration for StreamSnapper library."""

# Standard modules
from sys import stderr

# Third-party modules
from loguru import logger
from richuru import install as richuru_install


# Install richuru
richuru_install()

# Configure logger
logger.remove()
logger.add(
    stderr,
    level="DEBUG",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}</cyan> | <level>{message}</level>",
    colorize=True,
)
logger.add("streamsnapper.log", level="DEBUG")
