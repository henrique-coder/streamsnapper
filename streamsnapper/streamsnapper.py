# Built-in imports
from os import PathLike
from pathlib import Path
from re import sub as re_sub, compile as re_compile
from unicodedata import normalize
from locale import getlocale
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Callable, Union, Type

# Third-party imports
from pysmartdl2 import SmartDL
from scrapetube import get_search as scrape_youtube_search, get_playlist as scrape_youtube_playlist, get_channel as scrape_youtube_channel
from requests import head
from yt_dlp import YoutubeDL, utils as yt_dlp_utils
from sclib import SoundcloudAPI, Track as SoundcloudTrack

# Local imports
from .exceptions import *


def get_value(data: Dict[Any, Any], key: Any, fallback_key: Any = None, convert_to: Callable = None, default_to: Any = None) -> Any:
    """
    Get a value from a dictionary, with optional fallback key, conversion and default value.
    :param data: The dictionary to search for the key.
    :param key: The key to search for in the dictionary.
    :param fallback_key: The fallback key to search for in the dictionary if the main key is not found.
    :param convert_to: The type to convert the value to. If the conversion fails, return the default value. If None, return the value as is.
    :param default_to: The default value to return if the key is not found.
    :return: The value from the dictionary, or the default value if the key is not found.
    """

    try:
        value = data[key]
    except KeyError:
        if fallback_key is not None:
            try:
                value = data[fallback_key]
            except KeyError:
                return default_to
        else:
            return default_to

    if convert_to is not None:
        try:
            value = convert_to(value)
        except (ValueError, TypeError):
            return default_to

    return value

def format_string(query: str, max_length: int = 128) -> Optional[str]:
    """
    Format a string to be used as a filename or directory name. Remove special characters, limit length and normalize the string.
    :param query: The string to be formatted.
    :param max_length: The maximum length of the formatted string. If the string is longer, it will be truncated.
    :return: The formatted string. If the input string is empty or None, return None.
    """

    if not query:
        return None

    normalized_string = normalize('NFKD', query).encode('ASCII', 'ignore').decode('utf-8')
    sanitized_string = re_sub(r'\s+', ' ', re_sub(r'[^a-zA-Z0-9\-_()[\]{}!$#+;,. ]', '', normalized_string)).strip()

    if len(sanitized_string) > max_length:
        cutoff = sanitized_string[:max_length].rfind(' ')
        sanitized_string = sanitized_string[:cutoff] if cutoff != -1 else sanitized_string[:max_length]

    return sanitized_string if sanitized_string else None


class YouTube:
    """A class for extracting and formatting data from YouTube videos, facilitating access to general video information, video streams, audio streams and subtitles."""

    def __init__(self, enable_ytdlp_log: bool = True) -> None:
        """
        Initialize the Snapper class with optional settings for yt-dlp.
        :param enable_ytdlp_log: Enable or disable yt-dlp logging.
        """

        self._extractor: Type[YouTube.Extractor] = self.Extractor()
        enable_ytdlp_log = not enable_ytdlp_log

        self._ydl_opts: Dict[str, bool] = {'extract_flat': True, 'geo_bypass': True, 'noplaylist': True, 'age_limit': None, 'quiet': enable_ytdlp_log, 'no_warnings': enable_ytdlp_log, 'ignoreerrors': enable_ytdlp_log}
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

    def run(self, url: str = None, ytdlp_data: Dict[str, Any] = None) -> None:
        """
        Run the process of extracting and formatting data from a YouTube video.
        :param url: The YouTube video URL to extract data from.
        :param ytdlp_data: The raw yt-dlp data to extract and format. If provided, the URL will be ignored (useful for debugging and testing).
        :raises InvalidURLError: If no YouTube video URL is provided.
        :raises ScrapingError: If an error occurs while scraping the YouTube video.
        :raises InvalidDataError: If the yt-dlp data is invalid or missing required keys.
        """

        if ytdlp_data:
            self._raw_youtube_data = ytdlp_data
        elif not url:
            raise InvalidURLError('No YouTube video URL provided')
        else:
            video_id = self._extractor.extract_video_id(url)

            if not video_id:
                raise InvalidURLError(f'Invalid YouTube video URL: "{url}"')

            url = f'https://www.youtube.com/watch?v={video_id}'

            try:
                with YoutubeDL(self._ydl_opts) as ydl:
                    self._raw_youtube_data = ydl.extract_info(url, download=False, process=True)
            except (yt_dlp_utils.DownloadError, yt_dlp_utils.ExtractorError, Exception) as e:
                raise ScrapingError(f'Error occurred while scraping YouTube video: "{url}"') from e

        try:
            self._raw_youtube_streams = self._raw_youtube_data['formats']
            self._raw_youtube_subtitles = self._raw_youtube_data['subtitles']
        except KeyError as e:
            raise InvalidDataError(f'Invalid yt-dlp data. Missing required key: "{e.args[0]}"') from e

    def analyze_info(self) -> None:
        """
        Extract and format relevant information.
        """

        data = self._raw_youtube_data

        id_ = data.get('id')
        title = get_value(data, 'fulltitle', 'title')
        clean_title = format_string(title)
        channel_name = get_value(data, 'channel', 'uploader')
        clean_channel_name = format_string(channel_name)
        chapters = [
            {
                'title': chapter.get('title'),
                'startTime': get_value(chapter, 'start_time', convert_to=float),
                'endTime': get_value(chapter, 'end_time', convert_to=float)
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
            'description': data.get('description'),
            'channelId': data.get('channel_id'),
            'channelUrl': get_value(data, 'uploader_url', 'channel_url'),
            'channelName': channel_name,
            'cleanChannelName': clean_channel_name,
            'isVerifiedChannel': get_value(data, 'channel_is_verified', default_to=False),
            'duration': get_value(data, 'duration'),
            'viewCount': get_value(data, 'view_count'),
            'isAgeRestricted': get_value(data, 'age_limit', convert_to=bool),
            'categories': get_value(data, 'categories', default_to=[]),
            'tags': get_value(data, 'tags', default_to=[]),
            'isStreaming': get_value(data, 'is_live'),
            'uploadTimestamp': get_value(data, 'timestamp', 'release_timestamp'),
            'availability': get_value(data, 'availability'),
            'chapters': chapters,
            'commentCount': get_value(data, 'comment_count'),
            'likeCount': get_value(data, 'like_count'),
            'followCount': get_value(data, 'channel_follower_count'),
            'language': get_value(data, 'language'),
            'thumbnails': [
                f'https://img.youtube.com/vi/{id_}/maxresdefault.jpg',
                f'https://img.youtube.com/vi/{id_}/sddefault.jpg',
                f'https://img.youtube.com/vi/{id_}/hqdefault.jpg',
                f'https://img.youtube.com/vi/{id_}/mqdefault.jpg',
                f'https://img.youtube.com/vi/{id_}/default.jpg'
            ]
        }

        for thumbnail in general_info['thumbnails']:
            r = head(thumbnail, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}, allow_redirects=True, timeout=5)

            if r.status_code != 200:
                general_info['thumbnails'].remove(thumbnail)

        self.general_info = dict(sorted(general_info.items()))

    def analyze_video_streams(self, preferred_quality: Literal['all', 'best', '144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p', '4320p'] = 'all') -> None:
        """
        Extract and format the best video streams.
        :param preferred_quality: The preferred quality of the video stream. If "all", all streams will be considered and sorted by quality. If "best", only the best quality streams will be considered. If a specific quality is provided, the stream will be selected according to the chosen quality, however if the quality is not available, the best quality will be selected.
        """

        data = self._raw_youtube_streams

        format_id_extension_map = {
            702: 'mp4',     # AV1 HFR High - MP4 - 7680x4320
            402: 'mp4',     # AV1 HFR - MP4 - 7680x4320
            571: 'mp4',     # AV1 HFR - MP4 - 7680x4320
            272: 'webm',    # VP9 HFR - WEBM - 7680x4320
            701: 'mp4',     # AV1 HFR High - MP4 - 3840x2160
            401: 'mp4',     # AV1 HFR - MP4 - 3840x2160
            337: 'webm',    # VP9.2 HDR HFR - WEBM - 3840x2160
            315: 'webm',    # VP9 HFR - WEBM - 3840x2160
            313: 'webm',    # VP9 - WEBM - 3840x2160
            305: 'mp4',     # H.264 HFR - MP4 - 3840x2160
            266: 'mp4',     # H.264 - MP4 - 3840x2160
            700: 'mp4',     # AV1 HFR High - MP4 - 2560x1440
            400: 'mp4',     # AV1 HFR - MP4 - 2560x1440
            336: 'webm',    # VP9.2 HDR HFR - WEBM - 2560x1440
            308: 'webm',    # VP9 HFR - WEBM - 2560x1440
            271: 'webm',    # VP9 - WEBM - 2560x1440
            304: 'mp4',     # H.264 HFR - MP4 - 2560x1440
            264: 'mp4',     # H.264 - MP4 - 2560x1440
            699: 'mp4',     # AV1 HFR High - MP4 - 1920x1080
            399: 'mp4',     # AV1 HFR - MP4 - 1920x1080
            335: 'webm',    # VP9.2 HDR HFR - WEBM - 1920x1080
            303: 'webm',    # VP9 HFR - WEBM - 1920x1080
            248: 'webm',    # VP9 - WEBM - 1920x1080
            # 616: 'webm',  # VP9 - WEBM - 1920x1080 - YouTube Premium Format (M3U8)
            299: 'mp4',     # H.264 HFR - MP4 - 1920x1080
            137: 'mp4',     # H.264 - MP4 - 1920x1080
            216: 'mp4',     # H.264 - MP4 - 1920x1080
            170: 'webm',    # VP8 - WEBM - 1920x1080
            698: 'mp4',     # AV1 HFR High - MP4 - 1280x720
            398: 'mp4',     # AV1 HFR - MP4 - 1280x720
            334: 'webm',    # VP9.2 HDR HFR - WEBM - 1280x720
            302: 'webm',    # VP9 HFR - WEBM - 1280x720
            612: 'webm',    # VP9 HFR - WEBM - 1280x720
            247: 'webm',    # VP9 - WEBM - 1280x720
            298: 'mp4',     # H.264 HFR - MP4 - 1280x720
            136: 'mp4',     # H.264 - MP4 - 1280x720
            169: 'webm',    # VP8 - WEBM - 1280x720
            697: 'mp4',     # AV1 HFR High - MP4 - 854x480
            397: 'mp4',     # AV1 - MP4 - 854x480
            333: 'webm',    # VP9.2 HDR HFR - WEBM - 854x480
            244: 'webm',    # VP9 - WEBM - 854x480
            135: 'mp4',     # H.264 - MP4 - 854x480
            168: 'webm',    # VP8 - WEBM - 854x480
            696: 'mp4',     # AV1 HFR High - MP4 - 640x360
            396: 'mp4',     # AV1 - MP4 - 640x360
            332: 'webm',    # VP9.2 HDR HFR - WEBM - 640x360
            243: 'webm',    # VP9 - WEBM - 640x360
            134: 'mp4',     # H.264 - MP4 - 640x360
            167: 'webm',    # VP8 - WEBM - 640x360
            695: 'mp4',     # AV1 HFR High - MP4 - 426x240
            395: 'mp4',     # AV1 - MP4 - 426x240
            331: 'webm',    # VP9.2 HDR HFR - WEBM - 426x240
            242: 'webm',    # VP9 - WEBM - 426x240
            133: 'mp4',     # H.264 - MP4 - 426x240
            694: 'mp4',     # AV1 HFR High - MP4 - 256x144
            394: 'mp4',     # AV1 - MP4 - 256x144
            330: 'webm',    # VP9.2 HDR HFR - WEBM - 256x144
            278: 'webm',    # VP9 - WEBM - 256x144
            598: 'webm',    # VP9 - WEBM - 256x144
            160: 'mp4',     # H.264 - MP4 - 256x144
            597: 'mp4',     # H.264 - MP4 - 256x144
        }

        video_streams = [
            stream for stream in data
            if stream.get('vcodec') != 'none' and int(get_value(stream, 'format_id').split('-')[0]) in format_id_extension_map
        ]

        def calculate_score(stream: Dict[Any, Any]) -> float:
            width = stream.get('width', 0)
            height = stream.get('height', 0)
            framerate = stream.get('fps', 0)
            bitrate = stream.get('tbr', 0)

            return width * height * framerate * bitrate

        sorted_video_streams = sorted(video_streams, key=calculate_score, reverse=True)

        def extract_stream_info(stream: Dict[Any, Any]) -> Dict[str, Any]:
            codec = stream.get('vcodec', '')
            codec_parts = codec.split('.', 1)
            quality_note = stream.get('format_note')
            youtube_format_id = int(get_value(stream, 'format_id').split('-')[0])

            return {
                'url': stream.get('url'),
                'codec': codec_parts[0] if codec_parts else None,
                'codecVariant': codec_parts[1] if len(codec_parts) > 1 else None,
                'rawCodec': codec,
                'extension': format_id_extension_map.get(youtube_format_id, 'mp3'),
                'width': stream.get('width'),
                'height': stream.get('height'),
                'framerate': stream.get('fps'),
                'bitrate': stream.get('tbr'),
                'quality': stream.get('height'),
                'qualityNote': quality_note,
                'isHDR': 'hdr' in quality_note.lower() if quality_note else False,
                'size': stream.get('filesize'),
                'language': stream.get('language'),
                'youtubeFormatId': youtube_format_id
            }

        self.best_video_streams = [extract_stream_info(stream) for stream in sorted_video_streams] if sorted_video_streams else None
        self.best_video_stream = self.best_video_streams[0] if self.best_video_streams else None
        self.best_video_download_url = self.best_video_stream['url'] if self.best_video_stream else None

        self.available_video_qualities = list(dict.fromkeys([f'{stream['quality']}p' for stream in self.best_video_streams if stream['quality']]))

        if preferred_quality != 'all':
            preferred_quality = preferred_quality.strip().lower()

            if preferred_quality == 'best' or preferred_quality not in self.available_video_qualities:
                best_available_quality = max([stream['quality'] for stream in self.best_video_streams])
                self.best_video_streams = [stream for stream in self.best_video_streams if stream['quality'] == best_available_quality]
            else:
                self.best_video_streams = [stream for stream in self.best_video_streams if stream['quality'] == int(preferred_quality.replace('p', ''))]

            self.best_video_stream = self.best_video_streams[0] if self.best_video_streams else {}
            self.best_video_download_url = self.best_video_stream['url'] if self.best_video_stream else None

    def analyze_audio_streams(self, preferred_language: Union[str, Literal['all', 'original', 'auto']] = 'auto') -> None:
        """
        Extract and format the best audio streams.
        :param preferred_language: The preferred language code of the audio stream. If "all", all audio streams will be considered, regardless of language. If "original", only the original audios will be considered. If "auto", the language will be automatically selected according to the current operating system language (if not found or video is not available in that language, the fallback will be "original").
        """

        data = self._raw_youtube_streams

        format_id_extension_map = {
            338: 'webm',  # Opus - (VBR) ~480 KBPS - Quadraphonic (4)
            380: 'mp4',   # AC3 - 384 KBPS - Surround (5.1)
            328: 'mp4',   # EAC3 - 384 KBPS - Surround (5.1)
            325: 'mp4',   # DTSE (DTS Express) - 384 KBPS - Surround (5.1)
            258: 'mp4',   # AAC (LC) - 384 KBPS - Surround (5.1)
            327: 'mp4',   # AAC (LC) - 256 KBPS - Surround (5.1)
            141: 'mp4',   # AAC (LC) - 256 KBPS - Stereo (2)
            774: 'webm',  # Opus - (VBR) ~256 KBPS - Stereo (2)
            256: 'mp4',   # AAC (HE v1) - 192 KBPS - Surround (5.1)
            251: 'webm',  # Opus - (VBR) <=160 KBPS - Stereo (2)
            140: 'mp4',   # AAC (LC) - 128 KBPS - Stereo (2)
            250: 'webm',  # Opus - (VBR) ~70 KBPS - Stereo (2)
            249: 'webm',  # Opus - (VBR) ~50 KBPS - Stereo (2)
            139: 'mp4',   # AAC (HE v1) - 48 KBPS - Stereo (2)
            600: 'webm',  # Opus - (VBR) ~35 KBPS - Stereo (2)
            599: 'mp4',   # AAC (HE v1) - 30 KBPS - Stereo (2)
        }

        audio_streams = [
            stream for stream in data
            if stream.get('acodec') != 'none' and int(get_value(stream, 'format_id').split('-')[0]) in format_id_extension_map
        ]

        def calculate_score(stream: Dict[Any, Any]) -> float:
            bitrate = stream.get('abr', 0)
            sample_rate = stream.get('asr', 0)

            return bitrate * 0.1 + sample_rate / 1000

        sorted_audio_streams = sorted(audio_streams, key=calculate_score, reverse=True)

        def extract_stream_info(stream: Dict[Any, Any]) -> Dict[str, Any]:
            codec = stream.get('acodec', '')
            codec_parts = codec.split('.', 1)
            youtube_format_id = int(get_value(stream, 'format_id').split('-')[0])
            youtube_format_note = stream.get('format_note', '')

            return {
                'url': stream.get('url'),
                'codec': codec_parts[0] if codec_parts else None,
                'codecVariant': codec_parts[1] if len(codec_parts) > 1 else None,
                'rawCodec': codec,
                'extension': format_id_extension_map.get(youtube_format_id, 'mp3'),
                'bitrate': stream.get('abr'),
                'qualityNote': youtube_format_note,
                'isOriginalAudio': '(default)' in youtube_format_note or youtube_format_note.islower(),
                'size': stream.get('filesize'),
                'samplerate': stream.get('asr'),
                'channels': stream.get('audio_channels'),
                'language': stream.get('language'),
                'youtubeFormatId': youtube_format_id
            }

        self.best_audio_streams = [extract_stream_info(stream) for stream in sorted_audio_streams] if sorted_audio_streams else None
        self.best_audio_stream = self.best_audio_streams[0] if self.best_audio_streams else None
        self.best_audio_download_url = self.best_audio_stream['url'] if self.best_audio_stream else None

        self.available_audio_languages = list(dict.fromkeys([stream['language'].lower() for stream in self.best_audio_streams if stream['language']]))

        if preferred_language != 'all':
            preferred_language = preferred_language.strip().lower()

            if preferred_language == 'auto':
                try:
                    if self.system_language not in self.available_audio_languages:
                        raise ValueError

                    self.best_audio_streams = [stream for stream in self.best_audio_streams if stream['language'] == self.system_language]
                except ValueError:
                    preferred_language = 'original'
            if preferred_language == 'original':
                self.best_audio_streams = [stream for stream in self.best_audio_streams if stream['isOriginalAudio']]
            elif preferred_language != 'auto':
                self.best_audio_streams = [stream for stream in self.best_audio_streams if stream['language'] == preferred_language]

            self.best_audio_stream = self.best_audio_streams[0] if self.best_audio_streams else {}
            self.best_audio_download_url = self.best_audio_stream['url'] if self.best_audio_stream else None

    def analyze_subtitle_streams(self) -> None:
        """
        Extract and format the subtitle streams.
        """

        data = self._raw_youtube_subtitles

        subtitle_streams = {}

        for stream in data:
            subtitle_streams[stream] = [
                {
                    'extension': subtitle.get('ext'),
                    'url': subtitle.get('url'),
                    'language': subtitle.get('name')
                }
                for subtitle in data[stream]
            ]

        self.subtitle_streams = dict(sorted(subtitle_streams.items()))

    class Extractor:
        """A class for extracting data from YouTube URLs and searching for YouTube videos."""

        def __init__(self) -> None:
            """Initialize the Extractor class with some regular expressions for analyzing YouTube URLs."""

            self._platform_regex = re_compile(r'(?:https?://)?(?:www\.)?(music\.)?youtube\.com|youtu\.be')
            self._video_id_regex = re_compile(r'(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|v/|shorts/|music/|.*[?&]v=))([a-zA-Z0-9_-]{11})')
            self._playlist_id_regex = re_compile(r'(?:youtube\.com/(?:playlist\?list=|watch\?.*?&list=|music/playlist\?list=|music\.youtube\.com/watch\?.*?&list=))([a-zA-Z0-9_-]+)')

        def identify_platform(self, url: str) -> Optional[Literal['youtube', 'youtube_music']]:
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

        def extract_playlist_id(self, url: str) -> Optional[str]:
            """
            Extract the YouTube playlist ID from a URL. (Note: The playlist must be public).
            :param url: The URL to extract the playlist ID from.
            :return: The extracted playlist ID. If no playlist ID is found or the playlist is private, return None.
            """

            found_match = self._playlist_id_regex.search(url)
            return found_match.group(1) if found_match and len(found_match.group(1)) >= 34 else None

        def search(self, query: str, sort_by: Literal['relevance', 'upload_date', 'view_count', 'rating'] = 'relevance', results_type: Literal['video', 'channel', 'playlist', 'movie'] = 'video', limit: int = 1) -> Optional[List[str]]:
            """
            Search for YouTube videos, channels, playlists or movies.
            :param query: The search query to search for.
            :param sort_by: The sorting method to use for the search results.
            :param results_type: The type of results to search for.
            :param limit: The maximum number of video URLs to return.
            :return: A list of video URLs from the search results. If no videos are found, return None.
            """

            try:
                extracted_data = list(scrape_youtube_search(query=query, sleep=1, sort_by=sort_by, results_type=results_type, limit=limit))
            except Exception:
                return None

            if extracted_data:
                found_urls = [f'https://www.youtube.com/watch?v={item.get('videoId')}' for item in extracted_data if item.get('videoId')]
                return found_urls if found_urls else None

        def get_playlist_videos(self, url: str, limit: int = None) -> Optional[List[str]]:
            """
            Get the video URLs from a YouTube playlist.
            :param url: The URL of the YouTube playlist.
            :param limit: The maximum number of video URLs to return. If None, return all video URLs.
            :return: A list of video URLs from the playlist. If no videos are found or the playlist is private, return None.
            """

            playlist_id = self.extract_playlist_id(url)

            if not playlist_id:
                return None

            try:
                extracted_data = list(scrape_youtube_playlist(playlist_id, sleep=1, limit=limit))
            except Exception:
                return None

            if extracted_data:
                found_urls = [f'https://www.youtube.com/watch?v={item.get('videoId')}' for item in extracted_data if item.get('videoId')]
                return found_urls if found_urls else None

        def get_channel_videos(self, channel_id: str = None, channel_url: str = None, channel_username: str = None, sort_by: Literal['newest', 'oldest', 'popular'] = 'newest', content_type: Literal['videos', 'shorts', 'streams'] = 'videos', limit: int = None) -> Optional[List[str]]:
            """
            Get the video URLs from a YouTube channel.
            :param channel_id: The ID of the YouTube channel.
            :param channel_url: The URL of the YouTube channel.
            :param channel_username: The username of the YouTube channel.
            :param sort_by: The sorting method to use for the channel videos.
            :param content_type: The type of videos to get from the channel.
            :param limit: The maximum number of video URLs to return. If None, return all video URLs.
            :return: A list of video URLs from the channel. If no videos are found or the channel is non-existent, return None.
            """

            if sum([bool(channel_id), bool(channel_url), bool(channel_username)]) != 1:
                raise BadArgumentError('Provide only one of the following arguments: "channel_id", "channel_url" or "channel_username"')

            try:
                extracted_data = list(scrape_youtube_channel(channel_id=channel_id, channel_url=channel_url, channel_username=channel_username.replace('@', ''), sleep=1, sort_by=sort_by, content_type=content_type, limit=limit))
            except Exception:
                return None

            if extracted_data:
                found_urls = [f'https://www.youtube.com/watch?v={item.get('videoId')}' for item in extracted_data if item.get('videoId')]
                return found_urls if found_urls else None

class SoundCloud:
    """A class for extracting and formatting data from SoundCloud tracks and playlists, facilitating access to general track information and audio streams."""

    def __init__(self) -> None:
        """
        Initialize the SoundCloud class.
        """

        self._extractor: Type[SoundCloud.Extractor] = self.Extractor()
        self._soundcloud_api: SoundcloudAPI = SoundcloudAPI(client_id='gJUfQ83SeoGM0qvM3VetdqVTDyHmSusF')
        self._soundcloud_track: SoundcloudTrack = None

        self.general_info: Dict[str, Any] = {}
        self.best_audio_stream: Dict[str, Any] = {}
        self.best_audio_download_url: Optional[str] = None

    def run(self, url: str) -> None:
        """
        Run the process of extracting and formatting data from a SoundCloud track or playlist.
        :param url: The SoundCloud track or playlist URL to extract data from.
        :raises ScrapingError: If an error occurs while scraping the SoundCloud track.
        """

        try:
            self._soundcloud_track = self._soundcloud_api.resolve(url)
        except Exception as e:
            raise ScrapingError(f'Error occurred while scraping SoundCloud track: "{url}"') from e

    def analyze_info(self) -> None:
        """
        Extract and format relevant information.
        """

        self.general_info = {
            'id': self._soundcloud_track.id,
            'userId': self._soundcloud_track.user_id,
            'username': self._soundcloud_track.user['username'],
            'userAvatar': self._soundcloud_track.user['avatar_url'].replace('-large', '-original'),
            'title': self._soundcloud_track.title,
            'artist': self._soundcloud_track.artist,
            'duration': self._soundcloud_track.duration,
            'fullUrl': self._soundcloud_track.permalink_url,
            'thumbnail': self._soundcloud_track.artwork_url.replace('-large', '-original'),
            'commentCount': self._soundcloud_track.comment_count,
            'likeCount': self._soundcloud_track.likes_count,
            'downloadCount': self._soundcloud_track.download_count,
            'playbackCount': self._soundcloud_track.playback_count,
            'repostCount': self._soundcloud_track.reposts_count,
            'uploadTimestamp': int(datetime.fromisoformat(self._soundcloud_track.created_at.replace('Z', '+00:00')).timestamp()),
            'lastModifiedTimestamp': int(datetime.fromisoformat(self._soundcloud_track.last_modified.replace('Z', '+00:00')).timestamp()),
            'isCommentable': self._soundcloud_track.commentable,
            'description': self._soundcloud_track.description,
            'genre': self._soundcloud_track.genre,
            'tags': self._soundcloud_track.tag_list,
            'license': self._soundcloud_track.license,
        }

    def generate_audio_stream(self) -> None:
        """
        Extract and format the best audio stream.
        """

        self.best_audio_download_url = self._soundcloud_track.get_stream_url()

    class Extractor:
        """A class for extracting data from SoundCloud URLs and searching for SoundCloud tracks."""

        def __init__(self) -> None:
            """Initialize the Extractor class with some regular expressions for analyzing SoundCloud URLs."""

            self._track_id_regex = re_compile(r'(?:soundcloud\.com/|snd\.sc/)([^/]+)/(?!sets)([^/]+)')
            self._playlist_id_regex = re_compile(r'(?:soundcloud\.com/|snd\.sc/)([^/]+)/sets/([^/]+)')

        def extract_track_slug(self, url: str) -> Optional[str]:
            """
            Extract the SoundCloud track slug from a URL.
            :param url: The URL to extract the track slug from.
            :return: The extracted track slug. If no track slug is found, return None.
            """

            found_match = self._track_id_regex.search(url)
            return f'{found_match.group(1)}/{found_match.group(2)}' if found_match else None

        def extract_playlist_slug(self, url: str) -> Optional[str]:
            """
            Extract the SoundCloud playlist slug from a URL.
            :param url: The URL to extract the playlist slug from.
            :return: The extracted playlist slug. If no playlist slug is found, return None.
            """

            found_match = self._playlist_id_regex.search(url)
            return f'{found_match.group(1)}/sets/{found_match.group(2)}' if found_match else None

class Downloader:
    """
    A class for downloading direct download URLs. Created to download YouTube videos and audio streams. However, it can be used to download any direct download URL.
    """

    def __init__(self, url: str, output_file_path: Union[str, PathLike], max_connections: int = 4, show_progress_bar: bool = True, timeout: int = 120) -> None:
        """
        Initialize the Downloader class with the required settings for downloading a file.
        :param url: The download URL to download the file from.
        :param output_file_path: The path to save the downloaded file to. If the path is a directory, the file name will be generated from the URL (server response). If the path is a file, the file will be saved with the provided name.
        :param max_connections: The maximum number of connections (threads) to use for downloading the file.
        :param show_progress_bar: Show or hide the download progress bar.
        :param timeout: The maximum number of seconds to wait for the server to respond.
        """

        self._url: str = url
        self._output_file_path: Union[str, PathLike] = output_file_path
        self._max_connections: int = max_connections
        self._show_progress_bar: bool = show_progress_bar
        self._timeout: int = timeout

        self.output_downloaded_file_path: Optional[str] = None

    def download(self) -> None:
        """
        Download the file from the provided URL to the output file path.
        :raises DownloadError: If an error occurs while downloading the file.
        """

        try:
            downloader = SmartDL(urls=self._url, dest=self._output_file_path, threads=self._max_connections, progress_bar=self._show_progress_bar, timeout=self._timeout)
            downloader.start(blocking=True)
        except Exception as e:
            raise DownloadError(f'Error occurred while downloading URL: "{self._url}"') from e

        output_destination = downloader.get_dest()
        self.output_downloaded_file_path = Path(output_destination).resolve().as_posix() if output_destination else None
