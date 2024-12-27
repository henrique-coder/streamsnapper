# Built-in imports
from typing import List

# Local imports
from .exceptions import EmptyDataError, FFmpegNotFoundError, InvalidDataError, MergeError, ScrapingError, StreamSnapperError
from .merger import Merger
from .platforms.youtube import YouTube, YouTubeExtractor


__all__: List[str] = [
    'EmptyDataError',
    'FFmpegNotFoundError',
    'InvalidDataError',
    'MergeError',
    'ScrapingError',
    'StreamSnapperError',
    'Merger',
    'YouTube',
    'YouTubeExtractor',
]
