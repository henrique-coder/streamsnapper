# Local imports
from .platforms.youtube import YouTube, YouTubeExtractor
from .platforms.soundcloud import SoundCloud, SoundCloudExtractor
from .downloader import Downloader
from .merger import Merger
from .exceptions import StreamBaseError, EmptyDataError, InvalidDataError, ScrapingError, DownloadError, MergeError


__version__ = '0.2.0'
__license__ = 'MIT'

__all__ = [
    'YouTube',
    'YouTubeExtractor',
    'SoundCloud',
    'SoundCloudExtractor',
    'Downloader',
    'Merger',
    'StreamBaseError',
    'EmptyDataError',
    'InvalidDataError',
    'ScrapingError',
    'DownloadError',
    'MergeError',
]
