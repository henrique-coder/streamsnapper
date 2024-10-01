class StreamBaseError(Exception):
    """
    Base exception for StreamSnapper errors.
    """

    pass

class InvalidDataError(StreamBaseError):
    """
    Exception raised when invalid yt-dlp data is provided.
    """

    pass

class InvalidURLError(StreamBaseError):
    """
    Exception raised when an invalid URL is provided.
    """

    pass

class ScrapingError(StreamBaseError):
    """
    Exception raised when an error occurs while scraping YouTube data.
    """

    pass

class BadArgumentError(StreamBaseError):
    """
    Exception raised when an invalid argument is provided.
    """

    pass

class DownloadError(StreamBaseError):
    """
    Exception raised when an error occurs while downloading a file.
    """

    pass
