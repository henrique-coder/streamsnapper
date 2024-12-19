class StreamSnapperError(Exception):
    """Base class for all StreamSnapper exceptions."""

    pass


class EmptyDataError(StreamSnapperError):
    """Exception raised when no data is available."""

    pass


class FFmpegNotFoundError(StreamSnapperError):
    """Exception raised when the FFmpeg executable is not found."""

    pass


class InvalidDataError(StreamSnapperError):
    """Exception raised when invalid data is provided."""

    pass


class MergeError(StreamSnapperError):
    """Exception raised when an error occurs while merging files."""

    pass


class ScrapingError(StreamSnapperError):
    """Exception raised when an error occurs while scraping data."""

    pass
