# Built-in imports
from pathlib import Path
from random import choice
from typing import List, Optional, Tuple

# Third-party imports
from orjson import loads as orjson_loads
from pytest import fail, fixture, mark

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


class TestDownloader:
    @fixture
    def download_urls(self) -> List[str]:
        return ['https://httpbin.org/image/png', 'https://httpbin.org/image/svg', 'https://httpbin.org/image/webp']

    def test_file_download(self, download_urls: List[str]) -> None:
        downloader: Downloader = Downloader(
            max_connections='auto', connection_speed=1000, overwrite=True, show_progress_bar=True, custom_headers=None, timeout=10
        )

        try:
            downloader.download(url=choice(download_urls), output_path=Path.cwd())
        except (DownloadError, RequestError, StreamBaseError) as e:
            fail(f'Something went wrong while downloading a file. Error: {e}')


class TestMerger:
    def test_merger_initialization(self) -> None:
        try:
            Merger()
        except (FFmpegNotFoundError, MergeError, StreamBaseError) as e:
            fail(f'Something went wrong while initializing the Merger class. Error: {e}')


class TestYouTube:
    def test_video_data_extractor(self) -> None:
        youtube: YouTube = YouTube(logging=False)

        try:
            youtube.extract(ytdlp_data=orjson_loads(Path(Path(__file__).parent, 'assets/ytdlp_data.json').read_bytes()))
            youtube.analyze_info(check_thumbnails=False, retrieve_dislike_count=False)
            youtube.analyze_video_streams(preferred_quality='all')
            youtube.analyze_audio_streams(preferred_language='local')
            youtube.analyze_subtitle_streams()
        except (ValueError, InvalidDataError, ScrapingError, InvalidDataError, EmptyDataError, StreamBaseError) as e:
            fail(f'Something went wrong while extracting a YouTube video data. Error: {e}')

        assert youtube.general_info is not None, 'General information is not available.'
        assert youtube.best_video_streams is not None, 'Video streams are not available.'
        assert youtube.best_audio_streams is not None, 'Audio streams are not available.'
        assert youtube.subtitle_streams is not None, 'Subtitle streams are not available.'


class TestYouTubeExtractor:
    @fixture
    def youtube_extractor(self) -> YouTubeExtractor:
        return YouTubeExtractor()

    def test_platform_identifier(self, youtube_extractor: YouTubeExtractor) -> None:
        urls: List[Tuple[str, str]] = [
            ('https://music.youtube.com/watch?v=01234567890&list=RD012345678901234', 'youtubeMusic'),
            ('https://music.youtube.com/watch?v=01234567890', 'youtubeMusic'),
            ('https://www.youtube.com/watch?v=01234567890', 'youtube'),
            ('https://youtu.be/01234567890', 'youtube'),
        ]

        for url, expected_platform in urls:
            identified_platform = youtube_extractor.identify_platform(url)
            assert identified_platform == expected_platform, (
                f'URL: "{url}" - Identified platform: "{identified_platform}" - ' f'Expected platform: "{expected_platform}"'
            )

    def test_video_id_extractor(self, youtube_extractor: YouTubeExtractor) -> None:
        urls: List[Tuple[str, str]] = [
            ('https://www.youtube.com/watch?v=01234567890', '01234567890'),
            ('https://youtu.be/01234567890', '01234567890'),
            ('https://www.youtube.com/shorts/01234567890', '01234567890'),
            ('https://music.youtube.com/watch?v=01234567890', '01234567890'),
        ]

        for url, expected_video_id in urls:
            extracted_video_id = youtube_extractor.extract_video_id(url)
            assert extracted_video_id == expected_video_id, (
                f'URL: "{url}" - Extracted video ID: "{extracted_video_id}" - ' f'Expected video ID: "{expected_video_id}"'
            )

    def test_playlist_id_extractor(self, youtube_extractor: YouTubeExtractor) -> None:
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
            extracted_playlist_id = youtube_extractor.extract_playlist_id(url, include_private=False)
            assert extracted_playlist_id == expected_playlist_id, (
                f'Include Private: "False" - URL: "{urls}" - '
                f'Extracted playlist ID: "{extracted_playlist_id}" - '
                f'Expected playlist ID: "{expected_playlist_id}"'
            )

    @mark.skip(reason='CPU/Network heavy test, please run manually')
    def test_video_search(self) -> None:
        pass

    @mark.skip(reason='CPU/Network heavy test, please run manually')
    def test_playlist_videos_extractor(self) -> None:
        pass

    @mark.skip(reason='CPU/Network heavy test, please run manually')
    def test_channel_videos_extractor(self) -> None:
        pass
