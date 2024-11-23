# Built-in imports
from pathlib import Path
from os import PathLike
from threading import Thread
from contextlib import nullcontext
from mimetypes import guess_extension as guess_mimetype_extension
from queue import Queue
from typing import Union, Optional, Literal, Any, Dict

# Third-party imports
try:
    from requests import get, head
except (ImportError, ModuleNotFoundError):
    pass

try:
    from rich.progress import (
        Progress,
        BarColumn,
        DownloadColumn,
        TransferSpeedColumn,
        TimeRemainingColumn,
        TextColumn,
        TimeElapsedColumn,
    )
except (ImportError, ModuleNotFoundError):
    pass

# Local imports
from .exceptions import DownloadError


class Downloader:
    """A class for downloading direct download URLs. Created to download YouTube videos and audio streams. However, it can be used to download any direct download URL."""

    def __init__(
        self,
        max_connections: Union[int, Literal['auto']] = 'auto',
        overwrite: bool = False,
        show_progress_bar: bool = True,
        headers: Dict[Any, Any] = None,
        timeout: int = 1440,
    ) -> None:
        """
        Initialize the Downloader class with the required settings for downloading a file.

        :param max_connections: The maximum number of connections (threads) to use for downloading the file.
        :param overwrite: Overwrite the file if it already exists. Otherwise, a "_1", "_2", etc. suffix will be added to the file name.
        :param show_progress_bar: Show or hide the download progress bar.
        :param headers: A dictionary of custom headers to be sent with the request.
        :param timeout: The timeout in seconds for the download process.
        """

        if isinstance(max_connections, int) and max_connections <= 0:
            raise ValueError('The number of threads must be greater than 0.')

        self.max_connections = max_connections
        self._overwrite = overwrite
        self._show_progress_bar = show_progress_bar
        self._headers: Optional[Dict[Any, Any]] = headers
        self._timeout = timeout

        self._queue: Queue = Queue()

    def _generate_unique_filename(self, file_path: Union[str, PathLike]) -> Path:
        file_path = Path(file_path)

        if self._overwrite:
            return file_path

        counter = 1
        unique_filename = file_path

        while unique_filename.exists():
            unique_filename = Path(f'{file_path.parent}/{file_path.stem}_{counter}{file_path.suffix}')
            counter += 1

        return unique_filename

    def _get_filename_from_url(self, headers: Dict[Any, Any]) -> str:
        content_disposition = headers.get('Content-Disposition', '')

        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[-1].strip().strip('"')

            if filename:
                return filename

        mimetype = headers.get('Content-Type', '')

        if mimetype:
            extension = guess_mimetype_extension(mimetype.split(';')[0])

            if extension:
                return f'{mimetype.split('/')[0]}{extension}'

        return 'file.unknown'

    def _calculate_threads(self, file_size: int) -> int:
        if isinstance(self.max_connections, int):
            return self.max_connections

        if self.max_connections == 'auto':
            if file_size <= 5 * 1024 * 1024:  # < 5 MB
                return 4
            elif file_size <= 50 * 1024 * 1024:  # 5-50 MB
                return 8
            elif file_size <= 200 * 1024 * 1024:  # 50-200 MB
                return 16
            elif file_size <= 400 * 1024 * 1024:  # 200-400 MB
                return 24
            else:
                return 32

    def _download_chunk(self, url: str, start: int, end: int, temp_file: Union[str, PathLike]) -> None:
        headers = {} if self._headers is None else self._headers
        headers['Range'] = f'bytes={start}-{end}'

        r = get(url, headers=headers, stream=True, allow_redirects=True)

        with Path(temp_file).open('r+b') as f:
            f.seek(start)
            f.write(r.content)

    def _worker(self, progress_task_id: Optional[int] = None, progress: Optional[Progress] = None) -> None:
        while not self._queue.empty():
            task = self._queue.get()

            try:
                self._download_chunk(*task)

                if progress and progress_task_id is not None:
                    progress.update(progress_task_id, advance=task[2] - task[1] + 1)
            finally:
                self._queue.task_done()

    def download(self, url: str, output_file_path: Union[str, PathLike] = Path.cwd()) -> None:
        """
        Download a file from a given URL to a specified output path.

        :param url: The URL of the file to download.
        :param output_file_path: The path where the downloaded file will be saved. If it's a directory, the filename will be determined from the URL or server response. If it's a file path, it will save with that name. If overwrite=False and a conflict occurs, a unique name will be generated automatically (e.g., "file_1.ext"). If overwrite=True and a conflict occurs, existing files will be replaced without warning. Defaults to the current working directory.
        """

        output_file_path = Path(output_file_path).resolve()

        r = head(url, headers=self._headers, allow_redirects=True)

        if r.status_code != 200 or 'Content-Length' not in r.headers:
            raise ValueError('Could not determine the file size or access the URL.')

        file_size = int(r.headers['Content-Length'])
        filename = self._get_filename_from_url(r.headers)

        if output_file_path.is_dir():
            output_file_path = Path(output_file_path, filename)

        output_file_path.parent.mkdir(parents=True, exist_ok=True)
        unique_filename = self._generate_unique_filename(output_file_path)

        with open(unique_filename, 'wb') as f:
            f.write(b'\0' * file_size)

        threads_count = self._calculate_threads(file_size)
        chunk_size = file_size // threads_count

        for i in range(threads_count):
            start = i * chunk_size
            end = file_size - 1 if i == threads_count - 1 else (start + chunk_size - 1)
            temp_file = unique_filename
            self._queue.put((url, start, end, temp_file))

        mimetype = r.headers.get('Content-Type')

        context_manager = (
            Progress(
                TextColumn(f'Downloading a {mimetype.split("/")[0] if mimetype else "file"} ({mimetype or "unknown"})'),
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                TimeRemainingColumn(),
                TimeElapsedColumn(),
            )
            if self._show_progress_bar
            else nullcontext()
        )

        with context_manager as progress:
            task_id = None

            if self._show_progress_bar:
                task_id = progress.add_task('Downloading', total=file_size)

            threads = []

            for _ in range(threads_count):
                thread = Thread(
                    target=self._worker,
                    kwargs={'progress_task_id': task_id, 'progress': progress if self._show_progress_bar else None},
                )
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()
