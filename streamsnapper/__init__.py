# Built-in imports
from typing import List

# Local imports
from .downloader import Downloader
from .exceptions import (
    DownloadError,
    EmptyDataError,
    FFmpegNotFoundError,
    InvalidDataError,
    MergeError,
    RequestError,
    ScrapingError,
    StreamBaseError,
)
from .merger import Merger
from .platforms.youtube import YouTube, YouTubeExtractor


__all__: List[str] = [
    'Downloader',
    'DownloadError',
    'EmptyDataError',
    'FFmpegNotFoundError',
    'InvalidDataError',
    'MergeError',
    'RequestError',
    'ScrapingError',
    'StreamBaseError',
    'Merger',
    'YouTube',
    'YouTubeExtractor',
]
