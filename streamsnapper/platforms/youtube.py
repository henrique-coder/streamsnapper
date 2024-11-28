# Built-in imports
from locale import getlocale
from os import PathLike
from pathlib import Path
from re import compile as re_compile
from shutil import rmtree
from tempfile import gettempdir
from typing import Any, Dict, List, Literal, Optional, Union, Type
from urllib.parse import unquote

# Third-party imports
from requests import get, head
from scrapetube import (
    get_search as scrape_youtube_search,
    get_playlist as scrape_youtube_playlist,
    get_channel as scrape_youtube_channel,
)
from yt_dlp import YoutubeDL, utils as yt_dlp_utils

# Local imports
from ..downloader import Downloader
from ..exceptions import EmptyDataError, InvalidDataError, ScrapingError
from ..functions import get_value, format_string
from ..merger import Merger


class YouTube:
    """A class for extracting and formatting data from YouTube videos, facilitating access to general video information, video streams, audio streams and subtitles."""

    def __init__(self, logging: bool = False) -> None:
        """
        Initialize the YouTube class (provided by yt-dlp library).

        :param logging: Enable or disable yt-dlp logging.
        """

        self._extractor: Type[YouTubeExtractor] = YouTubeExtractor()

        logging = not logging

        self._ydl_opts: Dict[str, bool] = {
            'extract_flat': True,
            'geo_bypass': True,
            'noplaylist': True,
            'age_limit': None,
            'quiet': logging,
            'no_warnings': logging,
            'ignoreerrors': logging,
        }
        self._raw_youtube_data: Dict[Any, Any] = {}
        self._raw_youtube_streams: List[Dict[Any, Any]] = []
        self._raw_youtube_subtitles: Dict[str, List[Dict[str, str]]] = {}

        found_system_language = getlocale()

        if found_system_language:
            self.system_language: str = found_system_language[0].split('_')[0].lower()
        else:
            self.system_language: str = 'en'

        self.general_info: Dict[str, Any] = {}

        self.best_video_streams: List[Dict[str, Any]] = []
        self.best_video_stream: Dict[str, Any] = {}
        self.best_video_download_url: Optional[str] = None

        self.best_audio_streams: List[Dict[str, Any]] = []
        self.best_audio_stream: Dict[str, Any] = {}
        self.best_audio_download_url: Optional[str] = None

        self.subtitle_streams: Dict[str, List[Dict[str, str]]] = {}

        self.available_video_qualities: List[str] = []
        self.available_audio_languages: List[str] = []

    def extract(self, url: Optional[str] = None, ytdlp_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Extract general video information, video streams, audio streams and subtitles.

        :param url: The YouTube video URL to extract data from.
        :param ytdlp_data: The raw yt-dlp data to extract and format. If provided, the URL will be ignored (useful for debugging and testing).
        :raises ScrapingError: If an error occurs while scraping the YouTube video.
        :raises InvalidDataError: If the yt-dlp data is invalid or missing required keys.
        """

        if ytdlp_data:
            self._raw_youtube_data = ytdlp_data
        elif not url:
            raise ValueError('No YouTube video URL or yt-dlp data provided')
        else:
            video_id = self._extractor.extract_video_id(url)

            if not video_id:
                raise ValueError(f'Invalid YouTube video URL: "{url}"')

            url = f'https://www.youtube.com/watch?v={video_id}'

            try:
                with YoutubeDL(self._ydl_opts) as ydl:
                    self._raw_youtube_data = ydl.extract_info(url=url, download=False, process=True)
            except (yt_dlp_utils.DownloadError, yt_dlp_utils.ExtractorError, Exception) as e:
                raise ScrapingError(f'Error occurred while scraping YouTube video: "{url}"') from e

        self._raw_youtube_streams = get_value(self._raw_youtube_data, 'formats', convert_to=list)
        self._raw_youtube_subtitles = get_value(self._raw_youtube_data, 'subtitles', convert_to=dict, default_to={})

        if self._raw_youtube_streams is None:
            raise InvalidDataError('Invalid yt-dlp data. Missing required keys: "formats"')

    def analyze_info(self, check_thumbnails: bool = False, retrieve_dislike_count: bool = False) -> None:
        """
        Extract and format relevant information.

        :check_thumbnails: Whether thumbnails should be checked and removed if they are not available.
        :retrieve_dislike_count: Whether to retrieve the dislike count for the video. If False, the dislike count will be set to None.
        """

        data = self._raw_youtube_data

        id_ = get_value(data, 'id')
        title = get_value(data, 'title', ['fulltitle'])
        clean_title = format_string(title)
        description = get_value(data, 'description')
        channel_name = get_value(data, 'channel', ['uploader'])
        clean_channel_name = format_string(channel_name)
        chapters = [
            {
                'title': get_value(chapter, 'title'),
                'startTime': get_value(chapter, 'start_time', convert_to=float),
                'endTime': get_value(chapter, 'end_time', convert_to=float),
            }
            for chapter in get_value(data, 'chapters', convert_to=list, default_to=[])
        ]

        general_info = {
            'fullUrl': f'https://www.youtube.com/watch?v={id_}',
            'shortUrl': f'https://youtu.be/{id_}',
            'embedUrl': f'https://www.youtube.com/embed/{id_}',
            'id': id_,
            'title': title,
            'cleanTitle': clean_title,
            'description': description if description else None,
            'channelId': get_value(data, 'channel_id'),
            'channelUrl': get_value(data, 'channel_url', ['uploader_url']),
            'channelName': channel_name,
            'cleanChannelName': clean_channel_name,
            'isVerifiedChannel': get_value(data, 'channel_is_verified', default_to=False),
            'duration': get_value(data, 'duration'),
            'viewCount': get_value(data, 'view_count'),
            'isAgeRestricted': get_value(data, 'age_limit', convert_to=bool),
            'categories': get_value(data, 'categories', default_to=[]),
            'tags': get_value(data, 'tags', default_to=[]),
            'isStreaming': get_value(data, 'is_live'),
            'uploadTimestamp': get_value(data, 'timestamp', ['release_timestamp']),
            'availability': get_value(data, 'availability'),
            'chapters': chapters,
            'commentCount': get_value(data, 'comment_count', default_to=0),
            'likeCount': get_value(data, 'like_count'),
            'dislikeCount': get_value(
                get(
                    'https://returnyoutubedislikeapi.com/votes',
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
                    },
                    params={'videoId': id_},
                ).json(),
                'dislikes',
                convert_to=int,
            )
            if retrieve_dislike_count
            else None,
            'followCount': get_value(data, 'channel_follower_count'),
            'language': get_value(data, 'language'),
            'thumbnails': [
                f'https://img.youtube.com/vi/{id_}/maxresdefault.jpg',
                f'https://img.youtube.com/vi/{id_}/sddefault.jpg',
                f'https://img.youtube.com/vi/{id_}/hqdefault.jpg',
                f'https://img.youtube.com/vi/{id_}/mqdefault.jpg',
                f'https://img.youtube.com/vi/{id_}/default.jpg',
            ],
        }

        if check_thumbnails:
            while general_info['thumbnails']:
                if (
                    head(
                        general_info['thumbnails'][0],
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
                        },
                        allow_redirects=False,
                    ).status_code
                    == 200
                ):
                    break
                else:
                    general_info['thumbnails'].pop(0)

        self.general_info = dict(sorted(general_info.items()))

    def analyze_video_streams(
        self,
        preferred_quality: Literal['144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p', '4320p', 'all'] = 'all',
    ) -> None:
        """
        Extract and format the best video streams.

        :param preferred_quality: The preferred quality of the video stream. If a specific quality is provided, the stream will be selected according to the chosen quality, however if the quality is not available, the best quality will be selected. If "all", all streams will be considered and sorted by quality.
        """

        data = self._raw_youtube_streams

        format_id_extension_map = {
            702: 'mp4',  # AV1 HFR High - MP4 - 7680x4320
            402: 'mp4',  # AV1 HFR - MP4 - 7680x4320
            571: 'mp4',  # AV1 HFR - MP4 - 7680x4320
            272: 'webm',  # VP9 HFR - WEBM - 7680x4320
            701: 'mp4',  # AV1 HFR High - MP4 - 3840x2160
            401: 'mp4',  # AV1 HFR - MP4 - 3840x2160
            337: 'webm',  # VP9.2 HDR HFR - WEBM - 3840x2160
            315: 'webm',  # VP9 HFR - WEBM - 3840x2160
            313: 'webm',  # VP9 - WEBM - 3840x2160
            305: 'mp4',  # H.264 HFR - MP4 - 3840x2160
            266: 'mp4',  # H.264 - MP4 - 3840x2160
            700: 'mp4',  # AV1 HFR High - MP4 - 2560x1440
            400: 'mp4',  # AV1 HFR - MP4 - 2560x1440
            336: 'webm',  # VP9.2 HDR HFR - WEBM - 2560x1440
            308: 'webm',  # VP9 HFR - WEBM - 2560x1440
            271: 'webm',  # VP9 - WEBM - 2560x1440
            304: 'mp4',  # H.264 HFR - MP4 - 2560x1440
            264: 'mp4',  # H.264 - MP4 - 2560x1440
            699: 'mp4',  # AV1 HFR High - MP4 - 1920x1080
            399: 'mp4',  # AV1 HFR - MP4 - 1920x1080
            335: 'webm',  # VP9.2 HDR HFR - WEBM - 1920x1080
            303: 'webm',  # VP9 HFR - WEBM - 1920x1080
            248: 'webm',  # VP9 - WEBM - 1920x1080
            # 616: 'webm',  # VP9 - WEBM - 1920x1080 - YouTube Premium Format (M3U8)
            299: 'mp4',  # H.264 HFR - MP4 - 1920x1080
            137: 'mp4',  # H.264 - MP4 - 1920x1080
            216: 'mp4',  # H.264 - MP4 - 1920x1080
            170: 'webm',  # VP8 - WEBM - 1920x1080
            698: 'mp4',  # AV1 HFR High - MP4 - 1280x720
            398: 'mp4',  # AV1 HFR - MP4 - 1280x720
            334: 'webm',  # VP9.2 HDR HFR - WEBM - 1280x720
            302: 'webm',  # VP9 HFR - WEBM - 1280x720
            612: 'webm',  # VP9 HFR - WEBM - 1280x720
            247: 'webm',  # VP9 - WEBM - 1280x720
            298: 'mp4',  # H.264 HFR - MP4 - 1280x720
            136: 'mp4',  # H.264 - MP4 - 1280x720
            169: 'webm',  # VP8 - WEBM - 1280x720
            697: 'mp4',  # AV1 HFR High - MP4 - 854x480
            397: 'mp4',  # AV1 - MP4 - 854x480
            333: 'webm',  # VP9.2 HDR HFR - WEBM - 854x480
            244: 'webm',  # VP9 - WEBM - 854x480
            135: 'mp4',  # H.264 - MP4 - 854x480
            168: 'webm',  # VP8 - WEBM - 854x480
            696: 'mp4',  # AV1 HFR High - MP4 - 640x360
            396: 'mp4',  # AV1 - MP4 - 640x360
            332: 'webm',  # VP9.2 HDR HFR - WEBM - 640x360
            243: 'webm',  # VP9 - WEBM - 640x360
            134: 'mp4',  # H.264 - MP4 - 640x360
            167: 'webm',  # VP8 - WEBM - 640x360
            695: 'mp4',  # AV1 HFR High - MP4 - 426x240
            395: 'mp4',  # AV1 - MP4 - 426x240
            331: 'webm',  # VP9.2 HDR HFR - WEBM - 426x240
            242: 'webm',  # VP9 - WEBM - 426x240
            133: 'mp4',  # H.264 - MP4 - 426x240
            694: 'mp4',  # AV1 HFR High - MP4 - 256x144
            394: 'mp4',  # AV1 - MP4 - 256x144
            330: 'webm',  # VP9.2 HDR HFR - WEBM - 256x144
            278: 'webm',  # VP9 - WEBM - 256x144
            598: 'webm',  # VP9 - WEBM - 256x144
            160: 'mp4',  # H.264 - MP4 - 256x144
            597: 'mp4',  # H.264 - MP4 - 256x144
        }

        video_streams = [
            stream
            for stream in data
            if get_value(stream, 'vcodec') != 'none' and get_value(stream, 'format_id', convert_to=int) in format_id_extension_map
        ]

        def calculate_score(stream: Dict[Any, Any]) -> float:
            width = get_value(stream, 'width', 0, convert_to=int)
            height = get_value(stream, 'height', 0, convert_to=int)
            framerate = get_value(stream, 'fps', 0, convert_to=float)
            bitrate = get_value(stream, 'tbr', 0, convert_to=float)

            return float(width * height * framerate * bitrate)

        sorted_video_streams = sorted(video_streams, key=calculate_score, reverse=True)

        def extract_stream_info(stream: Dict[Any, Any]) -> Dict[str, Any]:
            codec = get_value(stream, 'vcodec')
            codec_parts = codec.split('.', 1) if codec else []
            quality_note = get_value(stream, 'format_note')
            youtube_format_id = get_value(stream, 'format_id', convert_to=int)

            data = {
                'url': unquote(get_value(stream, 'url')),
                'codec': codec_parts[0] if codec_parts else None,
                'codecVariant': codec_parts[1] if len(codec_parts) > 1 else None,
                'rawCodec': codec,
                'extension': get_value(format_id_extension_map, youtube_format_id, default_to='mp4'),
                'width': get_value(stream, 'width', convert_to=int),
                'height': get_value(stream, 'height', convert_to=int),
                'framerate': get_value(stream, 'fps', convert_to=float),
                'bitrate': get_value(stream, 'tbr', convert_to=float),
                'qualityNote': quality_note,
                'isHDR': 'hdr' in quality_note.lower() if quality_note else False,
                'size': get_value(stream, 'filesize', convert_to=int),
                'language': get_value(stream, 'language'),
                'youtubeFormatId': youtube_format_id,
            }

            data['quality'] = data['height']

            return dict(sorted(data.items()))

        self.best_video_streams = (
            [extract_stream_info(stream) for stream in sorted_video_streams] if sorted_video_streams else None
        )
        self.best_video_stream = self.best_video_streams[0] if self.best_video_streams else None
        self.best_video_download_url = self.best_video_stream['url'] if self.best_video_stream else None

        self.available_video_qualities = list(
            dict.fromkeys([f'{stream["quality"]}p' for stream in self.best_video_streams if stream['quality']])
        )

        if preferred_quality != 'all':
            preferred_quality = preferred_quality.strip().lower()

            if preferred_quality not in self.available_video_qualities:
                best_available_quality = max([stream['quality'] for stream in self.best_video_streams])
                self.best_video_streams = [
                    stream for stream in self.best_video_streams if stream['quality'] == best_available_quality
                ]
            else:
                self.best_video_streams = [
                    stream for stream in self.best_video_streams if stream['quality'] == int(preferred_quality.replace('p', ''))
                ]

            self.best_video_stream = self.best_video_streams[0] if self.best_video_streams else {}
            self.best_video_download_url = self.best_video_stream['url'] if self.best_video_stream else None

    def analyze_audio_streams(self, preferred_language: Union[str, Literal['source', 'local', 'all']] = 'local') -> None:
        """
        Extract and format the best audio streams.

        :param preferred_language: The preferred language code of the audio stream. If "source", only the source audios will be considered. If "auto", the language will be automatically selected according to the current operating system language (if not found or video is not available in that language, the fallback will be "source"). If "all", all audio streams will be considered, regardless of language.
        """

        data = self._raw_youtube_streams

        format_id_extension_map = {
            338: 'webm',  # Opus - (VBR) ~480 KBPS - Quadraphonic (4)
            380: 'mp4',  # AC3 - 384 KBPS - Surround (5.1)
            328: 'mp4',  # EAC3 - 384 KBPS - Surround (5.1)
            325: 'mp4',  # DTSE (DTS Express) - 384 KBPS - Surround (5.1)
            258: 'mp4',  # AAC (LC) - 384 KBPS - Surround (5.1)
            327: 'mp4',  # AAC (LC) - 256 KBPS - Surround (5.1)
            141: 'mp4',  # AAC (LC) - 256 KBPS - Stereo (2)
            774: 'webm',  # Opus - (VBR) ~256 KBPS - Stereo (2)
            256: 'mp4',  # AAC (HE v1) - 192 KBPS - Surround (5.1)
            251: 'webm',  # Opus - (VBR) <=160 KBPS - Stereo (2)
            140: 'mp4',  # AAC (LC) - 128 KBPS - Stereo (2)
            250: 'webm',  # Opus - (VBR) ~70 KBPS - Stereo (2)
            249: 'webm',  # Opus - (VBR) ~50 KBPS - Stereo (2)
            139: 'mp4',  # AAC (HE v1) - 48 KBPS - Stereo (2)
            600: 'webm',  # Opus - (VBR) ~35 KBPS - Stereo (2)
            599: 'mp4',  # AAC (HE v1) - 30 KBPS - Stereo (2)
        }

        audio_streams = [
            stream
            for stream in data
            if get_value(stream, 'acodec') != 'none' and get_value(stream, 'format_id', convert_to=int) in format_id_extension_map
        ]

        def calculate_score(stream: Dict[Any, Any]) -> float:
            bitrate = get_value(stream, 'abr', 0, convert_to=float)
            sample_rate = get_value(stream, 'asr', 0, convert_to=float)

            bitrate_priority = 0.1  # Change this value to adjust the bitrate priority (lower = higher bitrate priority)

            return float((bitrate * bitrate_priority) + (sample_rate / 1000))

        sorted_audio_streams = sorted(audio_streams, key=calculate_score, reverse=True)

        def extract_stream_info(stream: Dict[Any, Any]) -> Dict[str, Any]:
            codec = get_value(stream, 'acodec')
            codec_parts = codec.split('.', 1) if codec else []
            youtube_format_id = get_value(stream, 'format_id', convert_to=int)
            youtube_format_note = get_value(stream, 'format_note')

            data = {
                'url': unquote(get_value(stream, 'url')),
                'codec': codec_parts[0] if codec_parts else None,
                'codecVariant': codec_parts[1] if len(codec_parts) > 1 else None,
                'rawCodec': codec,
                'extension': get_value(format_id_extension_map, youtube_format_id, 'mp3'),
                'bitrate': get_value(stream, 'abr', convert_to=float),
                'qualityNote': youtube_format_note,
                'isOriginalAudio': '(default)' in youtube_format_note or youtube_format_note.islower()
                if youtube_format_note
                else None,
                'size': get_value(stream, 'filesize', convert_to=int),
                'samplerate': get_value(stream, 'asr', convert_to=int),
                'channels': get_value(stream, 'audio_channels', convert_to=int),
                'language': get_value(stream, 'language'),
                'youtubeFormatId': youtube_format_id,
            }

            return dict(sorted(data.items()))

        self.best_audio_streams = (
            [extract_stream_info(stream) for stream in sorted_audio_streams] if sorted_audio_streams else None
        )
        self.best_audio_stream = self.best_audio_streams[0] if self.best_audio_streams else None
        self.best_audio_download_url = self.best_audio_stream['url'] if self.best_audio_stream else None

        self.available_audio_languages = list(
            dict.fromkeys([stream['language'].lower() for stream in self.best_audio_streams if stream['language']])
        )

        if preferred_language != 'all':
            preferred_language = preferred_language.strip().lower()

            if preferred_language == 'local':
                if self.system_language in self.available_audio_languages:
                    self.best_audio_streams = [
                        stream for stream in self.best_audio_streams if stream['language'] == self.system_language
                    ]
                else:
                    preferred_language = 'source'
            if preferred_language == 'source':
                self.best_audio_streams = [stream for stream in self.best_audio_streams if stream['isOriginalAudio']]
            elif preferred_language != 'local':
                self.best_audio_streams = [
                    stream for stream in self.best_audio_streams if stream['language'] == preferred_language
                ]

            self.best_audio_stream = self.best_audio_streams[0] if self.best_audio_streams else {}
            self.best_audio_download_url = self.best_audio_stream['url'] if self.best_audio_stream else None

    def analyze_subtitle_streams(self) -> None:
        """Extract and format the subtitle streams."""

        data = self._raw_youtube_subtitles

        subtitle_streams = {}

        for stream in data:
            subtitle_streams[stream] = [
                {
                    'extension': get_value(subtitle, 'ext'),
                    'url': get_value(subtitle, 'url'),
                    'language': get_value(subtitle, 'name'),
                }
                for subtitle in data[stream]
            ]

        self.subtitle_streams = dict(sorted(subtitle_streams.items()))

    def download(
        self,
        video_stream: Optional[Dict[str, Any]] = None,
        audio_stream: Optional[Dict[str, Any]] = None,
        output_file_path: Union[str, PathLike] = Path.cwd(),
        show_progress_bar: bool = True,
        timeout: Optional[int] = 1440,
        logging: bool = False,
    ) -> Path:
        """
        Downloads specified video and/or audio streams. If both streams are provided, they will be downloaded and merged. If only one stream is provided, it will be downloaded without merging. If no streams are specified, the function will analyze and select default streams with optimized settings.

        :param video_stream: Video stream dictionary generated by the YouTube class.
        :param audio_stream: Audio stream dictionary generated by the YouTube class.
        :param output_file_path: The path to save the output file to. If the path is a directory, the file name will be generated automatically ({cleanTitle} [{id}].{extension}). If the path is a file, the file will be saved with the provided name. If not provided, the file will be saved to the current working directory.
        :param show_progress_bar: Show progress bar during download.
        :param timeout: Timeout in seconds for the download process. Or None for no timeout.
        :param logging: Enable or disable ffmpeg logging.
        :return: Path object of the output file.
        :raises EmptyDataError: If no YouTube data is available.
        """

        if not self._raw_youtube_data:
            raise EmptyDataError('No YouTube data available. Please call .extract() first.')

        if not self.general_info:
            self.analyze_info()

        if not video_stream and not audio_stream:
            self.analyze_video_streams()
            self.analyze_audio_streams()

            video_stream = self.best_video_stream
            audio_stream = self.best_audio_stream

        output_file_path = Path(output_file_path)

        if video_stream and audio_stream:
            if output_file_path.is_dir():
                output_file_path = Path(
                    output_file_path, f'{self.general_info["cleanTitle"]} [{self.general_info["id"]}].{video_stream["extension"]}'
                )

            tmp_path = Path(gettempdir(), '.tmp-streamsnapper-downloader')
            tmp_path.mkdir(exist_ok=True)

            output_video_file_path = Path(tmp_path, f'.tmp-video-{self.general_info["id"]}.{video_stream["extension"]}')
            video_downloader = Downloader(
                max_connections='auto', show_progress_bar=show_progress_bar, overwrite=True, timeout=timeout
            )
            video_downloader.download(video_stream['url'], output_video_file_path)

            output_audio_file_path = Path(tmp_path, f'.tmp-audio-{self.general_info["id"]}.{audio_stream["extension"]}')
            audio_downloader = Downloader(
                max_connections='auto', show_progress_bar=show_progress_bar, overwrite=True, timeout=timeout
            )
            audio_downloader.download(audio_stream['url'], output_audio_file_path)

            merger = Merger(logging=logging)
            merger.merge(
                video_file_path=output_video_file_path,
                audio_file_path=output_audio_file_path,
                output_file_path=output_file_path,
                ffmpeg_file_path='local',
            )

            rmtree(tmp_path)

            return output_file_path.resolve()
        elif video_stream:
            if output_file_path.is_dir():
                output_file_path = Path(
                    output_file_path, f'{self.general_info["cleanTitle"]} [{self.general_info["id"]}].{video_stream["extension"]}'
                )

            downloader = Downloader(max_connections='auto', show_progress_bar=show_progress_bar, overwrite=True, timeout=timeout)
            downloader.download(video_stream['url'], output_file_path)

            return Path(downloader.output_file_path)
        elif audio_stream:
            if output_file_path.is_dir():
                output_file_path = Path(
                    output_file_path, f'{self.general_info["cleanTitle"]} [{self.general_info["id"]}].{audio_stream["extension"]}'
                )

            downloader = Downloader(max_connections='auto', show_progress_bar=show_progress_bar, overwrite=True, timeout=timeout)
            downloader.download(audio_stream['url'], output_file_path)

            return Path(downloader.output_file_path)


class YouTubeExtractor:
    """A class for extracting data from YouTube URLs and searching for YouTube videos."""

    def __init__(self) -> None:
        """Initialize the Extractor class with some regular expressions for analyzing YouTube URLs."""

        self._platform_regex = re_compile(r'(?:https?://)?(?:www\.)?(music\.)?youtube\.com|youtu\.be|youtube\.com/shorts')
        self._video_id_regex = re_compile(
            r'(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|v/|shorts/|music/|live/|.*[?&]v=))([a-zA-Z0-9_-]{11})'
        )
        self._playlist_id_regex = re_compile(
            r'(?:youtube\.com/(?:playlist\?list=|watch\?.*?&list=|music/playlist\?list=|music\.youtube\.com/watch\?.*?&list=))([a-zA-Z0-9_-]+)'
        )

    def identify_platform(self, url: str) -> Optional[Literal['youtube', 'youtubeMusic']]:
        """
        Identify the platform of a URL (YouTube or YouTube Music).

        :param url: The URL to identify the platform from.
        :return: The identified platform. If the platform is not recognized, return None.
        """

        found_match = self._platform_regex.search(url)

        if found_match:
            return 'youtube_music' if found_match.group(1) else 'youtube'

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract the YouTube video ID from a URL.

        :param url: The URL to extract the video ID from.
        :return: The extracted video ID. If no video ID is found, return None.
        """

        found_match = self._video_id_regex.search(url)

        return found_match.group(1) if found_match else None

    def extract_playlist_id(self, url: str, include_private: bool = False) -> Optional[str]:
        """
        Extract the YouTube playlist ID from a URL.

        :param url: The URL to extract the playlist ID from.
        :param include_private: Whether to include private playlists, like the mixes YouTube makes for you.
        :return: The extracted playlist ID. If no playlist ID is found or the playlist is private, return None.
        """

        found_match = self._playlist_id_regex.search(url)

        if found_match:
            playlist_id = found_match.group(1)

            if not include_private:
                return playlist_id if len(playlist_id) == 34 else None

            return playlist_id if len(playlist_id) >= 34 or playlist_id.startswith('RD') else None

        return None

    def search(
        self,
        query: str,
        sort_by: Literal['relevance', 'upload_date', 'view_count', 'rating'] = 'relevance',
        results_type: Literal['video', 'channel', 'playlist', 'movie'] = 'video',
        limit: int = 1,
    ) -> Optional[List[str]]:
        """
        Search for YouTube videos, channels, playlists or movies (provided by scrapetube library).

        :param query: The search query to search for.
        :param sort_by: The sorting method to use for the search results.
        :param results_type: The type of results to search for.
        :param limit: The maximum number of video URLs to return.
        :return: A list of video URLs from the search results. If no videos are found, return None.
        """

        try:
            extracted_data = list(
                scrape_youtube_search(query=query, sleep=1, sort_by=sort_by, results_type=results_type, limit=limit)
            )
        except Exception:
            return None

        if extracted_data:
            found_urls = [
                f'https://www.youtube.com/watch?v={item.get("videoId")}' for item in extracted_data if item.get('videoId')
            ]

            return found_urls if found_urls else None

    def get_playlist_videos(self, url: str, limit: Optional[int] = None) -> Optional[List[str]]:
        """
        Get the video URLs from a YouTube playlist (provided by scrapetube library).

        :param url: The URL of the YouTube playlist.
        :param limit: The maximum number of video URLs to return. If None, return all video URLs.
        :return: A list of video URLs from the playlist. If no videos are found or the playlist is private, return None.
        """

        playlist_id = self.extract_playlist_id(url, include_private=False)

        if not playlist_id:
            return None

        try:
            extracted_data = list(scrape_youtube_playlist(playlist_id, sleep=1, limit=limit))
        except Exception:
            return None

        if extracted_data:
            found_urls = [
                f'https://www.youtube.com/watch?v={item.get("videoId")}' for item in extracted_data if item.get('videoId')
            ]

            return found_urls if found_urls else None

    def get_channel_videos(
        self,
        channel_id: Optional[str] = None,
        channel_url: Optional[str] = None,
        channel_username: Optional[str] = None,
        sort_by: Literal['newest', 'oldest', 'popular'] = 'newest',
        content_type: Literal['videos', 'shorts', 'streams'] = 'videos',
        limit: Optional[int] = None,
    ) -> Optional[List[str]]:
        """
        Get the video URLs from a YouTube channel (provided by scrapetube library).

        :param channel_id: The ID of the YouTube channel.
        :param channel_url: The URL of the YouTube channel.
        :param channel_username: The username of the YouTube channel.
        :param sort_by: The sorting method to use for the channel videos.
        :param content_type: The type of videos to get from the channel.
        :param limit: The maximum number of video URLs to return. If None, return all video URLs.
        :return: A list of video URLs from the channel. If no videos are found or the channel is non-existent, return None.
        """

        if sum([bool(channel_id), bool(channel_url), bool(channel_username)]) != 1:
            raise ValueError('Provide only one of the following arguments: "channel_id", "channel_url" or "channel_username"')

        try:
            extracted_data = list(
                scrape_youtube_channel(
                    channel_id=channel_id,
                    channel_url=channel_url,
                    channel_username=channel_username.replace('@', ''),
                    sleep=1,
                    sort_by=sort_by,
                    content_type=content_type,
                    limit=limit,
                )
            )
        except Exception:
            return None

        if extracted_data:
            found_urls = [
                f'https://www.youtube.com/watch?v={item.get("videoId")}' for item in extracted_data if item.get('videoId')
            ]

            return found_urls if found_urls else None
