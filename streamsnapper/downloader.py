# Built-in imports
from concurrent.futures import ThreadPoolExecutor
from math import ceil
from mimetypes import guess_extension as guess_mimetype_extension
from os import PathLike
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple, Union
from urllib.parse import unquote, urlparse

# Third-party imports
from requests import get, head, exceptions as requests_exceptions
from rich.progress import BarColumn, DownloadColumn, Progress, TextColumn, TimeRemainingColumn, TransferSpeedColumn

# Local imports
from .exceptions import DownloadError, RequestError


class Downloader:
    """A class for downloading direct download URLs."""

    def __init__(
        self,
        max_connections: Union[int, Literal['auto']] = 'auto',
        overwrite: bool = True,
        show_progress_bar: bool = True,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> None:
        """
        Initialize the Downloader class with the required settings for downloading a file.

        Args:
            max_connections: The maximum number of connections (threads) to use for downloading the file. (default: 'auto')
            overwrite: Overwrite the file if it already exists. Otherwise, a "_1", "_2", etc. suffix will be added. (default: True)
            show_progress_bar: Show or hide the download progress bar. (default: True)
            headers: Custom headers to include in the request. If None, default headers will be used. (default: None)
            timeout: Timeout in seconds for the download process. Or None for no timeout. (default: None)
        """

        self._max_connections: Union[int, Literal['auto']] = max_connections
        self._overwrite: bool = overwrite
        self._show_progress_bar: bool = show_progress_bar
        self._timeout: Optional[int] = timeout

        imutable_headers = ['Accept-Encoding', 'Range']

        self.headers: Dict[str, str] = {
            'Accept': '*/*',
            'Accept-Encoding': 'identity',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }

        if headers:
            for key, value in headers.items():
                if key.title() not in imutable_headers:
                    self.headers[key.title()] = value

        self.output_file_path: str = None

    def _calculate_connections(self, file_size: int) -> int:
        """
        Calculates the number of connections (threads) to use for downloading the file.

        The following table is used to determine the number of connections based on the file size:

        | File size       | Connections |
        |-----------------|-------------|
        | < 1 MB          | 1           |
        | 1 MB - 5 MB     | 4           |
        | 5 MB - 50 MB    | 8           |
        | 50 MB - 200 MB  | 16          |
        | 200 MB - 400 MB | 24          |
        | > 400 MB        | 32          |

        Args:
            file_size: The size of the file to download. (required)

        Returns:
            The number of connections to use.
        """

        if self._max_connections != 'auto':
            return self._max_connections

        if file_size < 1024 * 1024:
            return 1
        elif file_size <= 5 * 1024 * 1024:
            return 4
        elif file_size <= 50 * 1024 * 1024:
            return 8
        elif file_size <= 200 * 1024 * 1024:
            return 16
        elif file_size <= 400 * 1024 * 1024:
            return 24
        else:
            return 32

    def _get_file_info(self, url: str) -> Tuple[int, str, str]:
        """
        Retrieve file information from a given URL.

        This method sends a HEAD request to the specified URL to obtain the file's content length, content type, and filename.
        If the filename is not present in the 'Content-Disposition' header, it attempts to extract it from the URL path.
        If the filename cannot be determined, a default name with the appropriate extension is generated based on the content type.

        Args:
            url: The URL of the file to retrieve information from. (required)

        Returns:
            A tuple containing the content length (int), content type (str), and filename (str).

        Raises:
            RequestError: If an error occurs while sending the HEAD request.
        """

        try:
            r = head(url, headers=self.headers, timeout=self._timeout, allow_redirects=True)
        except requests_exceptions.RequestException as e:
            raise RequestError(f'An error occurred while getting file info: {str(e)}') from e

        content_length = int(r.headers.get('content-length', 0))
        content_type = r.headers.get('content-type', 'application/octet-stream').split(';')[0]
        content_disposition = r.headers.get('content-disposition')

        if content_disposition and 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[-1].strip('"\'')
        else:
            path = unquote(urlparse(url).path)
            filename = Path(path).name

            if not filename:
                extension = guess_mimetype_extension(content_type)

                if extension:
                    filename = 'downloaded_file' + extension

        return (content_length, content_type, filename)

    def _get_chunk_ranges(self, total_size: int) -> List[Tuple[int, int]]:
        """
        Calculate and return the chunk ranges for downloading a file.

        This method divides the total file size into smaller chunks based on the number of connections calculated.
        Each chunk is represented as a tuple containing the start and end byte positions.

        Args:
            total_size: The total size of the file to be downloaded. (required)

        Returns:
            A list of tuples, where each tuple contains the start and end positions (in bytes) for each chunk.
            If the total size is zero, returns a single chunk with both start and end as zero.
        """

        if total_size == 0:
            return [(0, 0)]

        connections = self._calculate_connections(total_size)
        chunk_size = ceil(total_size / connections)
        ranges = []

        for i in range(0, total_size, chunk_size):
            end = min(i + chunk_size - 1, total_size - 1)
            ranges.append((i, end))

        return ranges

    def _download_chunk(self, url: str, start: int, end: int, progress: Progress, task_id: int) -> bytes:
        """
        Downloads a chunk of a file from the given URL.

        This method sends a GET request with a 'Range' header to the specified URL to obtain the specified chunk of the file.
        The chunk is then returned as bytes.

        Args:
            url: The URL to download the chunk from. (required)
            start: The start byte of the chunk. (required)
            end: The end byte of the chunk. (required)
            progress: The Progress object to update with the chunk's size. (required)
            task_id: The task ID to update in the Progress object. (required)

        Returns:
            The downloaded chunk as bytes.

        Raises:
            DownloadError: If an error occurs while downloading the chunk.
        """

        headers = {**self.headers}

        if end > 0:
            headers['Range'] = f'bytes={start}-{end}'

        try:
            response = get(url, headers=headers, timeout=self._timeout)
            response.raise_for_status()

            chunk = response.content
            progress.update(task_id, advance=len(chunk))

            return chunk
        except requests_exceptions.RequestException as e:
            raise DownloadError(f'An error occurred while downloading chunk: {str(e)}') from e

    def download(self, url: str, output_path: Union[str, PathLike] = Path.cwd()) -> None:
        """
        Downloads a file from the provided URL to the output file path.

        If the output_path is a directory, the file name will be generated from the server response.
        If the output_path is a file, the file will be saved with the provided name.
        If not provided, the file will be saved to the current working directory.

        Args:
            url: The download URL to download the file from. (required)
            output_path: The path to save the downloaded file to. If the path is a directory, the file name will be generated from the server response. If the path is a file, the file will be saved with the provided name. If not provided, the file will be saved to the current working directory. (default: Path.cwd())

        Raises:
            DownloadError: If an error occurs while downloading the file.
        """

        try:
            total_size, mime_type, suggested_filename = self._get_file_info(url)
            output_path = Path(output_path)

            if output_path.is_dir():
                output_path = Path(output_path, suggested_filename)

            if not self._overwrite:
                base_name = output_path.stem
                extension = output_path.suffix
                counter = 1

                while output_path.exists():
                    output_path = Path(output_path.parent, f'{base_name}_{counter}{extension}')
                    counter += 1

            self.output_file_path = output_path.as_posix()

            progress_columns = [
                TextColumn(f'Downloading a {mime_type.split("/")[0] if mime_type else "unknown"} file ({mime_type})'),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeRemainingColumn(),
            ]

            with Progress(*progress_columns, disable=not self._show_progress_bar) as progress:
                task_id = progress.add_task('download', total=total_size or 100, filename=output_path.name, mime=mime_type)

                if total_size == 0:
                    chunk = self._download_chunk(url, 0, 0, progress, task_id)

                    with Path(output_path).open('wb') as fo:
                        fo.write(chunk)
                else:
                    chunks = []
                    ranges = self._get_chunk_ranges(total_size)
                    connections = len(ranges)

                    with ThreadPoolExecutor(max_workers=connections) as executor:
                        futures = [
                            executor.submit(self._download_chunk, url, start, end, progress, task_id) for start, end in ranges
                        ]
                        chunks = [f.result() for f in futures]

                    with Path(output_path).open('wb') as fo:
                        for chunk in chunks:
                            fo.write(chunk)
        except Exception as e:
            raise DownloadError(f'An error occurred while downloading file: {str(e)}') from e
