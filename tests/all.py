# Built-in imports
from pathlib import Path
from random import choice

# Third-party imports
from unittest import TestCase, main
from rich.console import Console

# Local imports
from streamsnapper import (
    Downloader,
    DownloadError,
    EmptyDataError,
    FFmpegNotFoundError,
    InvalidDataError,
    MergeError,
    Merger,
    RequestError,
    ScrapingError,
    StreamBaseError,
    YouTube,
    YouTubeExtractor,
)


console = Console()


class TestDownloader(TestCase):
    def setUp(self: TestCase) -> None:
        self.test_download_urls = [
            'https://httpbin.org/image/jpeg',
            'https://httpbin.org/image/png',
            'https://httpbin.org/image/svg',
            'https://httpbin.org/image/webp',
        ]

    def test_download_file(self: TestCase) -> None:
        downloader = Downloader(max_connections='auto', overwrite=True, show_progress_bar=True, headers=None, timeout=10)

        try:
            downloader.download(url=choice(self.test_download_urls), output_path=Path.cwd())
        except (DownloadError, RequestError, StreamBaseError) as e:
            self.fail(f'Something went wrong while downloading a file. Error: {e}')


class TestMerger(TestCase):
    def test_merger_init(self: TestCase) -> None:
        try:
            Merger()
        except (FFmpegNotFoundError, MergeError, StreamBaseError) as e:
            self.fail(f'Something went wrong while initializing the Merger class. Error: {e}')


class TestYouTube(TestCase):
    pass


class TestYouTubeExtractor(TestCase):
    pass


if __name__ == '__main__':
    main()
