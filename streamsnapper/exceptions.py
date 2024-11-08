class StreamBaseError(Exception):
    """Base exception for StreamSnapper errors."""

    pass


class EmptyDataError(StreamBaseError):
    """Exception raised when no data is available."""

    pass


class InvalidDataError(StreamBaseError):
    """Exception raised when invalid data is provided."""

    pass


class ScrapingError(StreamBaseError):
    """Exception raised when an error occurs while scraping data."""

    pass


class DownloadError(StreamBaseError):
    """Exception raised when an error occurs while downloading a file."""

    pass


class MergeError(StreamBaseError):
    """Exception raised when an error occurs while merging files."""

    pass
