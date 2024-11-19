# Built-in imports
from pathlib import Path
from os import PathLike
from typing import Optional, Union

# Third-party imports
try:
    from pysmartdl2 import SmartDL
except (ImportError, ModuleNotFoundError):
    pass

# Local imports
from .exceptions import DownloadError


class Downloader:
    """A class for downloading direct download URLs. Created to download YouTube videos and audio streams. However, it can be used to download any direct download URL."""

    def __init__(self, max_connections: int = 4, show_progress_bar: bool = True, timeout: int = 14400) -> None:
        """
        Initialize the Downloader class with the required settings for downloading a file.

        :param max_connections: The maximum number of connections (threads) to use for downloading the file.
        :param show_progress_bar: Show or hide the download progress bar.
        :param timeout: The timeout in seconds for the download process.
        """

        self._max_connections: int = max_connections
        self._show_progress_bar: bool = show_progress_bar
        self._timeout: int = timeout

        self.output_file_path: Optional[str] = None

    def download(self, url: str, output_file_path: Union[str, PathLike] = Path.cwd()) -> None:
        """
        Download the file from the provided URL to the output file path.

        :param url: The download URL to download the file from.
        :param output_file_path: The path to save the downloaded file to. If the path is a directory, the file name will be generated from the server response. If the path is a file, the file will be saved with the provided name. If not provided, the file will be saved to the current working directory.
        :raises DownloadError: If an error occurs while downloading the file.
        """

        output_file_path = Path(output_file_path).resolve()

        try:
            downloader = SmartDL(
                urls=url,
                dest=output_file_path.as_posix(),
                threads=self._max_connections,
                progress_bar=self._show_progress_bar,
                timeout=self._timeout,
            )
            downloader.start(blocking=True)
        except Exception as e:
            raise DownloadError(f'Error occurred while downloading URL: "{url}" to "{output_file_path.as_posix()}"') from e

        output_destination = downloader.get_dest()
        self.output_file_path = Path(output_destination).as_posix() if output_file_path else None
