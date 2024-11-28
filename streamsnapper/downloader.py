# Built-in imports
from concurrent.futures import ThreadPoolExecutor
from math import ceil
from mimetypes import guess_extension as guess_mimetype_extension
from os import PathLike
from pathlib import Path
from typing import Union, Literal, Optional, Dict, List, Tuple
from urllib.parse import urlparse, unquote

# Third-party imports
from requests import get, head, exceptions as requests_exceptions
from rich.progress import Progress, DownloadColumn, TransferSpeedColumn, TextColumn, TimeRemainingColumn, BarColumn

# Local imports
from .exceptions import DownloadError


class Downloader:
    """A class for downloading direct download URLs."""

    def __init__(
        self,
        max_connections: Union[int, Literal['auto']] = 'auto',
        overwrite: bool = True,
        show_progress_bar: bool = True,
        timeout: Optional[int] = 1440,
    ) -> None:
        """
        Initialize the Downloader class with the required settings for downloading a file.

        :param max_connections: The maximum number of connections (threads) to use for downloading the file.
        :param overwrite: Overwrite the file if it already exists. Otherwise, a "_1", "_2", etc. suffix will be added.
        :param show_progress_bar: Show or hide the download progress bar.
        :param timeout: Timeout in seconds for the download process. Or None for no timeout.
        """

        self._max_connections: Union[int, Literal['auto']] = max_connections
        self._overwrite: bool = overwrite
        self._show_progress_bar: bool = show_progress_bar
        self._timeout: Optional[int] = timeout
        self._headers: Dict[str, str] = {
            'Accept': '*/*',
            'Accept-Encoding': 'identity',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        }

        self.output_file_path: str = None

    def _calculate_connections(self, file_size: int) -> int:
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

    def _get_file_info(self, url: str) -> tuple[int, str, str]:
        try:
            response = head(url, headers=self._headers, timeout=self._timeout, allow_redirects=True)

            if response.status_code == 405:
                response = get(url, headers=self._headers, timeout=self._timeout, stream=True)

            response.raise_for_status()

            content_length = int(response.headers.get('content-length', 0))
            content_type = response.headers.get('content-type', 'application/octet-stream').split(';')[0]

            content_disp = response.headers.get('content-disposition')

            if content_disp and 'filename=' in content_disp:
                filename = content_disp.split('filename=')[-1].strip('"\'')
            else:
                path = unquote(urlparse(url).path)
                filename = Path(path).name

                if not filename:
                    extension = guess_mimetype_extension(content_type)

                    if extension:
                        filename = 'downloaded_file' + extension

            return content_length, content_type, filename

        except requests_exceptions.RequestException as e:
            raise DownloadError(f'An error occurred while getting file info: {str(e)}') from e

    def _get_chunk_ranges(self, total_size: int) -> List[Tuple[int, int]]:
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
        headers = {**self._headers}

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

    def download(self, url: str, output_file_path: Union[str, PathLike] = Path.cwd()) -> None:
        """
        Downloads specified file from the given URL.

        :param url: The URL to download from.
        :param output_file_path: The file path to save the downloaded file to. If it's a directory, the file name will be generated from the server response. Defaults to the current working directory.
        :raises DownloadError: If an error occurs while downloading the file.
        """

        try:
            total_size, mime_type, suggested_filename = self._get_file_info(url)

            output_path = Path(output_file_path)

            if output_path.is_dir():
                output_path = Path(output_path, suggested_filename)

            if not self._overwrite:
                base, ext = output_path.stem, output_path.suffix
                counter = 1

                while output_path.exists():
                    output_path = Path(output_path.parent, f'{base}_{counter}{ext}')
                    counter += 1

            self.output_file_path = output_path.as_posix()

            progress_columns = [
                TextColumn(f'Downloading "{output_path.name}" ({mime_type})'),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeRemainingColumn(),
            ]

            with Progress(*progress_columns, disable=not self._show_progress_bar) as progress:
                task_id = progress.add_task('download', total=total_size or 100, filename=output_path.name, mime=mime_type)

                if total_size == 0:
                    chunk = self._download_chunk(url, 0, 0, progress, task_id)

                    with open(output_path, 'wb') as f:
                        f.write(chunk)
                else:
                    chunks = []
                    ranges = self._get_chunk_ranges(total_size)
                    connections = len(ranges)

                    with ThreadPoolExecutor(max_workers=connections) as executor:
                        futures = [
                            executor.submit(self._download_chunk, url, start, end, progress, task_id) for start, end in ranges
                        ]
                        chunks = [f.result() for f in futures]

                    with open(output_path, 'wb') as f:
                        for chunk in chunks:
                            f.write(chunk)
        except Exception as e:
            raise DownloadError(f'An error occurred while downloading file: {str(e)}') from e
