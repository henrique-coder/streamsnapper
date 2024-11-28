# Local imports
from .platforms.youtube import YouTube, YouTubeExtractor
from .downloader import Downloader
from .merger import Merger
from .exceptions import StreamBaseError, EmptyDataError, InvalidDataError, ScrapingError, DownloadError, MergeError


__version__ = '0.2.2-dev'
__license__ = 'MIT'

__all__ = [
    'YouTube',
    'YouTubeExtractor',
    'Downloader',
    'Merger',
    'StreamBaseError',
    'EmptyDataError',
    'InvalidDataError',
    'ScrapingError',
    'DownloadError',
    'MergeError',
]
