class StreamBaseError(Exception):
    """Base exception for StreamSnapper errors."""

    pass


class InvalidDataError(StreamBaseError):
    """Exception raised when invalid yt-dlp data is provided."""

    pass


class ScrapingError(StreamBaseError):
    """Exception raised when an error occurs while scraping YouTube data."""

    pass


class DownloadError(StreamBaseError):
    """Exception raised when an error occurs while downloading a file."""

    pass


class MergeError(StreamBaseError):
    """Exception raised when an error occurs while merging files."""

    pass
