# Built-in imports
from pathlib import Path
from random import choice
from typing import List, Optional, Tuple
from unittest import TestCase, main

# Third-party imports
from orjson import loads as orjson_loads
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
        self.test_download_urls: List[str] = [
            'https://httpbin.org/image/jpeg',
            'https://httpbin.org/image/png',
            'https://httpbin.org/image/svg',
            'https://httpbin.org/image/webp',
        ]

    def test_file_download(self: TestCase) -> None:
        downloader: Downloader = Downloader(
            max_connections='auto', overwrite=True, show_progress_bar=True, headers=None, timeout=10
        )

        try:
            downloader.download(url=choice(self.test_download_urls), output_path=Path.cwd())
        except (DownloadError, RequestError, StreamBaseError) as e:
            self.fail(f'Something went wrong while downloading a file. Error: {e}')


class TestMerger(TestCase):
    def test_merger_initialization(self: TestCase) -> None:
        try:
            Merger()
        except (FFmpegNotFoundError, MergeError, StreamBaseError) as e:
            self.fail(f'Something went wrong while initializing the Merger class. Error: {e}')


class TestYouTube(TestCase):
    def test_video_data_extractor(self: TestCase) -> None:
        youtube: YouTube = YouTube(logging=False)

        try:
            youtube.extract(ytdlp_data=orjson_loads(Path(Path(__file__).parent, 'assets/ytdlp_data.json').read_bytes()))
            youtube.analyze_info(check_thumbnails=False, retrieve_dislike_count=False)
            youtube.analyze_video_streams(preferred_quality='all')
            youtube.analyze_audio_streams(preferred_language='local')
            youtube.analyze_subtitle_streams()
        except (ValueError, InvalidDataError, ScrapingError, InvalidDataError, EmptyDataError, StreamBaseError) as e:
            self.fail(f'Something went wrong while extracting a YouTube video data. Error: {e}')

        self.assertIsNotNone(youtube.general_info, 'General information is not available.')
        self.assertIsNotNone(youtube.best_video_streams, 'Video streams are not available.')
        self.assertIsNotNone(youtube.best_audio_streams, 'Audio streams are not available.')
        self.assertIsNotNone(youtube.subtitle_streams, 'Subtitle streams are not available.')


class TestYouTubeExtractor(TestCase):
    def setUp(self: TestCase) -> None:
        self.youtube_extractor: YouTubeExtractor = YouTubeExtractor()

    def test_platform_identifier(self: TestCase) -> None:
        urls: List[Tuple[str, str]] = [
            ('https://music.youtube.com/watch?v=01234567890&list=RD012345678901234', 'youtubeMusic'),
            ('https://music.youtube.com/watch?v=01234567890', 'youtubeMusic'),
            ('https://www.youtube.com/watch?v=01234567890', 'youtube'),
            ('https://youtu.be/01234567890', 'youtube'),
        ]

        for url, expected_platform in urls:
            identified_platform = self.youtube_extractor.identify_platform(url)
            self.assertEqual(
                identified_platform,
                expected_platform,
                f'URL: "{url}" - Identified platform: "{identified_platform}" - Expected platform: "{expected_platform}"',
            )

    def test_video_id_extractor(self: TestCase) -> None:
        urls: List[Tuple[str, str]] = [
            ('https://www.youtube.com/watch?v=01234567890', '01234567890'),
            ('https://youtu.be/01234567890', '01234567890'),
            ('https://www.youtube.com/shorts/01234567890', '01234567890'),
            ('https://music.youtube.com/watch?v=01234567890', '01234567890'),
        ]

        for url, expected_video_id in urls:
            extracted_video_id = self.youtube_extractor.extract_video_id(url)
            self.assertEqual(
                extracted_video_id,
                expected_video_id,
                f'URL: "{url}" - Extracted video ID: "{extracted_video_id}" - Expected video ID: "{expected_video_id}"',
            )

    def test_playlist_id_extractor(self: TestCase) -> None:
        urls: List[Tuple[str, Optional[str]]] = [
            ('https://youtu.be/01234567890', None),
            ('https://music.youtube.com/watch?v=01234567890&list=RD012345678901234', None),
            ('https://music.youtube.com/playlist?list=RD123456789123456', None),
            ('https://www.youtube.com/playlist?list=0123456789012345678901234567890123', '0123456789012345678901234567890123'),
            (
                'https://www.youtube.com/watch?v=01234567890&list=0123456789012345678901234567890123',
                '0123456789012345678901234567890123',
            ),
        ]

        for url, expected_playlist_id in urls:
            extracted_playlist_id = self.youtube_extractor.extract_playlist_id(url, include_private=False)
            self.assertEqual(
                extracted_playlist_id,
                expected_playlist_id,
                f'Include Private: "False" - URL: "{urls}" - Extracted playlist ID: "{extracted_playlist_id}" - Expected playlist ID: "{expected_playlist_id}"',
            )

    def test_video_search(self: TestCase) -> None:
        pass  # CPU/Network heavy test - Skipped

    def test_playlist_videos_extractor(self: TestCase) -> None:
        pass  # CPU/Network heavy test - Skipped

    def test_channel_videos_extractor(self: TestCase) -> None:
        pass  # CPU/Network heavy test - Skipped


if __name__ == '__main__':
    main()
