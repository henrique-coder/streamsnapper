class StreamBaseError(Exception):
    """Base exception for StreamSnapper errors."""

    pass


class DownloadError(StreamBaseError):
    """Exception raised when an error occurs while downloading a file."""

    pass


class EmptyDataError(StreamBaseError):
    """Exception raised when no data is available."""

    pass


class FFmpegNotFoundError(StreamBaseError):
    """Exception raised when the FFmpeg executable is not found."""

    pass


class InvalidDataError(StreamBaseError):
    """Exception raised when invalid data is provided."""

    pass


class MergeError(StreamBaseError):
    """Exception raised when an error occurs while merging files."""

    pass


class RequestError(StreamBaseError):
    """Exception raised when an error occurs while making a request."""

    pass


class ScrapingError(StreamBaseError):
    """Exception raised when an error occurs while scraping data."""

    pass
