class StreamSnapperError(Exception):
    """Base class for all StreamSnapper exceptions"""

    pass


class InvalidDataError(StreamSnapperError):
    """Exception raised when invalid data is provided"""

    pass


class ScrapingError(StreamSnapperError):
    """Exception raised when an error occurs while scraping data"""

    pass
