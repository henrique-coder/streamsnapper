# Built-in imports
from json import JSONDecodeError
from locale import getlocale
from os import PathLike
from pathlib import Path
from re import compile as re_compile
from shutil import rmtree
from tempfile import gettempdir
from typing import Any, Dict, List, Literal, Optional, Type, Union
from urllib.parse import unquote

# Third-party imports
from httpx import get, head
from scrapetube import (
    get_search as scrape_youtube_search,
    get_playlist as scrape_youtube_playlist,
    get_channel as scrape_youtube_channel,
)
from turbodl import TurboDL
from yt_dlp import YoutubeDL
from yt_dlp import utils as yt_dlp_utils

# Local imports
from .exceptions import EmptyDataError, InvalidDataError, ScrapingError
from .functions import format_string, get_value, strip
from .merger import Merger


class InformationStructure:
    """
    A class for storing information about a YouTube video.
    """

    def __init__(self) -> None:
        """
        Initialize the Information class.
        """

        self._sourceUrl: Optional[str] = None
        self._shortUrl: Optional[str] = None
        self._embedUrl: Optional[str] = None
        self._youtubeMusicUrl: Optional[str] = None
        self._fullUrl: Optional[str] = None
        self._id: Optional[str] = None
        self._title: Optional[str] = None
        self._cleanTitle: Optional[str] = None
        self._description: Optional[str] = None
        self._channelId: Optional[str] = None
        self._channelUrl: Optional[str] = None
        self._channelName: Optional[str] = None
        self._cleanChannelName: Optional[str] = None
        self._isVerifiedChannel: Optional[bool] = None
        self._duration: Optional[int] = None
        self._viewCount: Optional[int] = None
        self._isAgeRestricted: Optional[bool] = None
        self._categories: Optional[List[str]] = None
        self._tags: Optional[List[str]] = None
        self._isStreaming: Optional[bool] = None
        self._uploadTimestamp: Optional[int] = None
        self._availability: Optional[str] = None
        self._chapters: Optional[List[Dict[str, Union[str, float]]]] = None
        self._commentCount: Optional[int] = None
        self._likeCount: Optional[int] = None
        self._dislikeCount: Optional[int] = None
        self._followCount: Optional[int] = None
        self._language: Optional[str] = None
        self._thumbnails: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the information to a dictionary, sorted by keys.

        Returns:
            A dictionary containing the information, alphabetically ordered.
        """

        return dict(sorted({key[1:]: value for key, value in self.__dict__.items()}.items()))

    @property
    def sourceUrl(self) -> Optional[str]:
        """
        Get the source URL of the video.

        Returns:
            The source URL of the video.
        """

        return self._source_url

    @property
    def shortUrl(self) -> Optional[str]:
        """
        Get the short URL of the video.

        Returns:
            The short URL of the video.
        """

        return self._short_url

    @property
    def embedUrl(self) -> Optional[str]:
        """
        Get the embed URL of the video.

        Returns:
            The embed URL of the video.
        """

        return self._embedUrl

    @property
    def youtubeMusicUrl(self) -> Optional[str]:
        """
        Get the YouTube Music URL of the video.

        Returns:
            The YouTube Music URL of the video.
        """

        return self._youtubeMusicUrl

    @property
    def fullUrl(self) -> Optional[str]:
        """
        Get the full URL of the video.

        Returns:
            The full URL of the video.
        """

        return self._fullUrl

    @property
    def id(self) -> Optional[str]:
        """
        Get the ID of the video.

        Returns:
            The ID of the video.
        """

        return self._id

    @property
    def title(self) -> Optional[str]:
        """
        Get the title of the video.

        Returns:
            The title of the video.
        """

        return self._title

    @property
    def cleanTitle(self) -> Optional[str]:
        """
        Get the clean title of the video.

        Returns:
            The clean title of the video.
        """

        return self._cleanTitle

    @property
    def description(self) -> Optional[str]:
        """
        Get the description of the video.

        Returns:
            The description of the video.
        """

        return self._description

    @property
    def channelId(self) -> Optional[str]:
        """
        Get the ID of the channel that uploaded the video.

        Returns:
            The ID of the channel that uploaded the video.
        """

        return self._channelId

    @property
    def channelUrl(self) -> Optional[str]:
        """
        Get the URL of the channel that uploaded the video.

        Returns:
            The URL of the channel that uploaded the video.
        """

        return self._channelUrl

    @property
    def channelName(self) -> Optional[str]:
        """
        Get the name of the channel that uploaded the video.

        Returns:
            The name of the channel that uploaded the video.
        """

        return self._channelName

    @property
    def cleanChannelName(self) -> Optional[str]:
        """
        Get the clean name of the channel that uploaded the video.

        Returns:
            The clean name of the channel that uploaded the video.
        """

        return self._cleanChannelName

    @property
    def isVerifiedChannel(self) -> Optional[bool]:
        """
        Get whether the channel that uploaded the video is verified.

        Returns:
            Whether the channel that uploaded the video is verified.
        """

        return self._isVerifiedChannel

    @property
    def duration(self) -> Optional[int]:
        """
        Get the duration of the video in seconds.

        Returns:
            The duration of the video in seconds.
        """

        return self._duration

    @property
    def viewCount(self) -> Optional[int]:
        """
        Get the view count of the video.

        Returns:
            The view count of the video.
        """

        return self._viewCount

    @property
    def isAgeRestricted(self) -> Optional[bool]:
        """
        Get whether the video is age restricted.

        Returns:
            Whether the video is age restricted.
        """

        return self._isAgeRestricted

    @property
    def categories(self) -> Optional[List[str]]:
        """
        Get the categories of the video.

        Returns:
            The categories of the video.
        """

        return self._categories

    @property
    def tags(self) -> Optional[List[str]]:
        """
        Get the tags of the video.

        Returns:
            The tags of the video.
        """

        return self._tags

    @property
    def isStreaming(self) -> Optional[bool]:
        """
        Get whether the video is streaming.

        Returns:
            Whether the video is streaming.
        """

        return self._isStreaming

    @property
    def uploadTimestamp(self) -> Optional[int]:
        """
        Get the upload timestamp of the video.

        Returns:
            The upload timestamp of the video.
        """

        return self._uploadTimestamp

    @property
    def availability(self) -> Optional[str]:
        """
        Get the availability of the video.

        Returns:
            The availability of the video.
        """

        return self._availability

    @property
    def chapters(self) -> Optional[List[Dict[str, Union[str, float]]]]:
        """
        Get the chapters of the video.

        Returns:
            The chapters of the video.
        """

        return self._chapters

    @property
    def commentCount(self) -> Optional[int]:
        """
        Get the comment count of the video.

        Returns:
            The comment count of the video.
        """

        return self._commentCount

    @property
    def likeCount(self) -> Optional[int]:
        """
        Get the like count of the video.

        Returns:
            The like count of the video.
        """

        return self._likeCount

    @property
    def dislikeCount(self) -> Optional[int]:
        """
        Get the dislike count of the video.

        Returns:
            The dislike count of the video.
        """

        return self._dislikeCount

    @property
    def followCount(self) -> Optional[int]:
        """
        Get the follow count of the video.

        Returns:
            The follow count of the video.
        """

        return self._followCount

    @property
    def language(self) -> Optional[str]:
        """
        Get the language of the video.

        Returns:
            The language of the video.
        """

        return self._language

    @property
    def thumbnails(self) -> Optional[List[str]]:
        """
        Get the thumbnails of the video.

        Returns:
            The thumbnails of the video.
        """

        return self._thumbnails


class YouTube:
    """
    A class for extracting and formatting data from YouTube videos, facilitating access to general video information, video streams, audio streams and subtitles.
    """

    def __init__(self, logging: bool = False) -> None:
        """
        Initialize the YouTube class with the required settings for extracting and formatting data from YouTube videos (raw data provided by yt-dlp library).

        Args:
            logging: Enable or disable logging for the YouTube class. Defaults to False. (default: False)
        """

        logging = not logging

        self._ydl_opts: Dict[str, bool] = {
            "extract_flat": True,
            "geo_bypass": True,
            "noplaylist": True,
            "age_limit": None,
            "ignoreerrors": True,
            "quiet": logging,
            "no_warnings": logging,
        }
        self._extractor: Type[YouTubeExtractor] = YouTubeExtractor()
        self._raw_youtube_data: Dict[Any, Any] = {}
        self._raw_youtube_streams: List[Dict[Any, Any]] = []
        self._raw_youtube_subtitles: Dict[str, List[Dict[str, str]]] = {}

        found_system_language = getlocale()[0]

        if found_system_language:
            try:
                self.base_system_language: str = found_system_language.split("_")[0].lower()
                self.system_language_suffix: str = found_system_language.split("_")[1].upper()
            except IndexError:
                self.base_system_language: str = "en"
                self.system_language_suffix: str = "US"
        else:
            self.base_system_language: str = "en"
            self.system_language_suffix: str = "US"

        self.information: Type[InformationStructure] = InformationStructure()

        self.best_video_streams: List[Dict[str, Any]] = []
        self.best_video_stream: Dict[str, Any] = {}
        self.best_video_download_url: Optional[str] = None

        self.best_audio_streams: List[Dict[str, Any]] = []
        self.best_audio_stream: Dict[str, Any] = {}
        self.best_audio_download_url: Optional[str] = None

        self.subtitle_streams: Dict[str, List[Dict[str, str]]] = {}

        self.available_video_qualities: List[str] = []
        self.available_audio_languages: List[str] = []

    def extract(self, url: Optional[str] = None, ytdlp_data: Optional[Dict[Any, Any]] = None) -> None:
        """
        Extract the YouTube video data from a URL or provided previously extracted yt-dlp data.

        - If a URL is provided, it will be used to scrape the YouTube video data.
        - If yt-dlp data is provided, it will be used directly.
        - If both URL and yt-dlp data are provided, the yt-dlp data will be used.

        Args:
            url: The YouTube video URL to extract data from. (default: None)
            ytdlp_data: The previously extracted yt-dlp data. (default: None)

        Raises:
            ValueError: If no URL or yt-dlp data is provided.
            InvalidDataError: If the provided yt-dlp data is invalid.
            ScrapingError: If an error occurs while scraping the YouTube video.
        """

        self._source_url = url

        if ytdlp_data:
            self._raw_youtube_data = ytdlp_data
        elif not url:
            raise ValueError("No YouTube video URL or yt-dlp data provided")
        else:
            video_id = self._extractor.extract_video_id(url)

            if not video_id:
                raise ValueError(f'Invalid YouTube video URL: "{url}"')

            try:
                with YoutubeDL(self._ydl_opts) as ydl:
                    self._raw_youtube_data = ydl.extract_info(url=url, download=False, process=True)
            except (yt_dlp_utils.DownloadError, yt_dlp_utils.ExtractorError, Exception) as e:
                raise ScrapingError(f'Error occurred while scraping YouTube video: "{url}"') from e

        self._raw_youtube_streams = get_value(self._raw_youtube_data, "formats", convert_to=list)
        self._raw_youtube_subtitles = get_value(self._raw_youtube_data, "subtitles", convert_to=dict, default_to={})

        if self._raw_youtube_streams is None:
            raise InvalidDataError('Invalid yt-dlp data. Missing required keys: "formats"')

    def analyze_information(self, check_thumbnails: bool = False, retrieve_dislike_count: bool = False) -> None:
        """
        Analyze the information of the YouTube video.

        Args:
            check_thumbnails: Check if all video thumbnails are available. (default: False)
            retrieve_dislike_count: Retrieve the dislike count from the returnyoutubedislike.com API. (default: False)

        Raises:
            InvalidDataError: If the provided yt-dlp data is invalid.
        """

        data = self._raw_youtube_data

        id_ = get_value(data, "id")
        title = get_value(data, "fulltitle", ["title"])
        clean_title = format_string(title)
        description = get_value(data, "description")
        channel_name = get_value(data, "channel", ["uploader"])
        clean_channel_name = format_string(channel_name)
        chapters = [
            {
                "title": get_value(chapter, "title"),
                "startTime": get_value(chapter, "start_time", convert_to=float),
                "endTime": get_value(chapter, "end_time", convert_to=float),
            }
            for chapter in get_value(data, "chapters", convert_to=list, default_to=[])
        ]

        dislike_count = None

        if retrieve_dislike_count:
            r = get(
                "https://returnyoutubedislikeapi.com/votes",
                params={"videoId": id_},
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
                },
            )

            if r.is_success:
                try:
                    dislike_count = get_value(r.json(), "dislikes", convert_to=int)
                except JSONDecodeError:
                    pass

        self.information._sourceUrl = self._source_url
        self.information._shortUrl = f"https://youtu.be/{id_}"
        self.information._embedUrl = f"https://www.youtube.com/embed/{id_}"
        self.information._youtubeMusicUrl = f"https://music.youtube.com/watch?v={id_}"
        self.information._fullUrl = f"https://www.youtube.com/watch?v={id_}"
        self.information._id = id_
        self.information._title = title
        self.information._cleanTitle = clean_title
        self.information._description = description if description else None
        self.information._channelId = get_value(data, "channel_id")
        self.information._channelUrl = get_value(data, "channel_url", ["uploader_url"])
        self.information._channelName = channel_name
        self.information._cleanChannelName = clean_channel_name
        self.information._isVerifiedChannel = get_value(data, "channel_is_verified", default_to=False)
        self.information._duration = get_value(data, "duration")
        self.information._viewCount = get_value(data, "view_count")
        self.information._isAgeRestricted = get_value(data, "age_limit", convert_to=bool)
        self.information._categories = get_value(data, "categories", default_to=[])
        self.information._tags = get_value(data, "tags", default_to=[])
        self.information._isStreaming = get_value(data, "is_live")
        self.information._uploadTimestamp = get_value(data, "timestamp", ["release_timestamp"])
        self.information._availability = get_value(data, "availability")
        self.information._chapters = chapters
        self.information._commentCount = get_value(data, "comment_count", convert_to=int, default_to=0)
        self.information._likeCount = get_value(data, "like_count", convert_to=int)
        self.information._dislikeCount = dislike_count
        self.information._followCount = get_value(data, "channel_follower_count", convert_to=int)
        self.information._language = get_value(data, "language")
        self.information._thumbnails = [
            f"https://img.youtube.com/vi/{id_}/maxresdefault.jpg",
            f"https://img.youtube.com/vi/{id_}/sddefault.jpg",
            f"https://img.youtube.com/vi/{id_}/hqdefault.jpg",
            f"https://img.youtube.com/vi/{id_}/mqdefault.jpg",
            f"https://img.youtube.com/vi/{id_}/default.jpg",
        ]

        if check_thumbnails:
            while self.information._thumbnails:
                if head(
                    self.information._thumbnails[0],
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
                    },
                    follow_redirects=False,
                ).is_success:
                    break
                else:
                    self.information._thumbnails.pop(0)

    def analyze_video_streams(
        self,
        preferred_quality: Literal["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "4320p", "all"] = "all",
    ) -> None:
        """
        Analyze the video streams of the YouTube video and select the best stream based on the preferred quality.

        Args:
            preferred_quality: The preferred quality of the video stream. If a specific quality is provided, the stream will be selected according to the chosen quality, however if the quality is not available, the best quality will be selected. If 'all', all streams will be considered and sorted by quality. (default: 'all')
        """

        data = self._raw_youtube_streams

        format_id_extension_map = {
            702: "mp4",  # AV1 HFR High - MP4 - 7680x4320
            402: "mp4",  # AV1 HFR - MP4 - 7680x4320
            571: "mp4",  # AV1 HFR - MP4 - 7680x4320
            272: "webm",  # VP9 HFR - WEBM - 7680x4320
            701: "mp4",  # AV1 HFR High - MP4 - 3840x2160
            401: "mp4",  # AV1 HFR - MP4 - 3840x2160
            337: "webm",  # VP9.2 HDR HFR - WEBM - 3840x2160
            315: "webm",  # VP9 HFR - WEBM - 3840x2160
            313: "webm",  # VP9 - WEBM - 3840x2160
            305: "mp4",  # H.264 HFR - MP4 - 3840x2160
            266: "mp4",  # H.264 - MP4 - 3840x2160
            700: "mp4",  # AV1 HFR High - MP4 - 2560x1440
            400: "mp4",  # AV1 HFR - MP4 - 2560x1440
            336: "webm",  # VP9.2 HDR HFR - WEBM - 2560x1440
            308: "webm",  # VP9 HFR - WEBM - 2560x1440
            271: "webm",  # VP9 - WEBM - 2560x1440
            304: "mp4",  # H.264 HFR - MP4 - 2560x1440
            264: "mp4",  # H.264 - MP4 - 2560x1440
            699: "mp4",  # AV1 HFR High - MP4 - 1920x1080
            399: "mp4",  # AV1 HFR - MP4 - 1920x1080
            335: "webm",  # VP9.2 HDR HFR - WEBM - 1920x1080
            303: "webm",  # VP9 HFR - WEBM - 1920x1080
            248: "webm",  # VP9 - WEBM - 1920x1080
            # 616: 'webm',  # VP9 - WEBM - 1920x1080 - YouTube Premium Format (M3U8)
            299: "mp4",  # H.264 HFR - MP4 - 1920x1080
            137: "mp4",  # H.264 - MP4 - 1920x1080
            216: "mp4",  # H.264 - MP4 - 1920x1080
            170: "webm",  # VP8 - WEBM - 1920x1080
            698: "mp4",  # AV1 HFR High - MP4 - 1280x720
            398: "mp4",  # AV1 HFR - MP4 - 1280x720
            334: "webm",  # VP9.2 HDR HFR - WEBM - 1280x720
            302: "webm",  # VP9 HFR - WEBM - 1280x720
            612: "webm",  # VP9 HFR - WEBM - 1280x720
            247: "webm",  # VP9 - WEBM - 1280x720
            298: "mp4",  # H.264 HFR - MP4 - 1280x720
            136: "mp4",  # H.264 - MP4 - 1280x720
            169: "webm",  # VP8 - WEBM - 1280x720
            697: "mp4",  # AV1 HFR High - MP4 - 854x480
            397: "mp4",  # AV1 - MP4 - 854x480
            333: "webm",  # VP9.2 HDR HFR - WEBM - 854x480
            244: "webm",  # VP9 - WEBM - 854x480
            135: "mp4",  # H.264 - MP4 - 854x480
            168: "webm",  # VP8 - WEBM - 854x480
            696: "mp4",  # AV1 HFR High - MP4 - 640x360
            396: "mp4",  # AV1 - MP4 - 640x360
            332: "webm",  # VP9.2 HDR HFR - WEBM - 640x360
            243: "webm",  # VP9 - WEBM - 640x360
            134: "mp4",  # H.264 - MP4 - 640x360
            167: "webm",  # VP8 - WEBM - 640x360
            695: "mp4",  # AV1 HFR High - MP4 - 426x240
            395: "mp4",  # AV1 - MP4 - 426x240
            331: "webm",  # VP9.2 HDR HFR - WEBM - 426x240
            242: "webm",  # VP9 - WEBM - 426x240
            133: "mp4",  # H.264 - MP4 - 426x240
            694: "mp4",  # AV1 HFR High - MP4 - 256x144
            394: "mp4",  # AV1 - MP4 - 256x144
            330: "webm",  # VP9.2 HDR HFR - WEBM - 256x144
            278: "webm",  # VP9 - WEBM - 256x144
            598: "webm",  # VP9 - WEBM - 256x144
            160: "mp4",  # H.264 - MP4 - 256x144
            597: "mp4",  # H.264 - MP4 - 256x144
        }

        video_streams = [
            stream
            for stream in data
            if get_value(stream, "vcodec") != "none" and get_value(stream, "format_id", convert_to=int) in format_id_extension_map
        ]

        def calculate_score(stream: Dict[Any, Any]) -> float:
            """
            Calculate a score for a given video stream.

            - The score is a product of the stream's width, height, framerate, and bitrate.
            - The score is used to sort the streams in order of quality.

            Args:
                stream: The video stream to calculate the score for. (required)

            Returns:
                The calculated score for the stream.
            """

            width = get_value(stream, "width", 0, convert_to=int)
            height = get_value(stream, "height", 0, convert_to=int)
            framerate = get_value(stream, "fps", 0, convert_to=float)
            bitrate = get_value(stream, "tbr", 0, convert_to=float)

            return float(width * height * framerate * bitrate)

        sorted_video_streams = sorted(video_streams, key=calculate_score, reverse=True)

        def extract_stream_info(stream: Dict[Any, Any]) -> Dict[str, Optional[Union[str, int, float, bool]]]:
            """
            Extract the information of a given video stream.

            Args:
                stream: The video stream to extract the information from. (required)

            Returns:
                A dictionary containing the extracted information of the stream.
            """

            codec = get_value(stream, "vcodec")
            codec_parts = codec.split(".", 1) if codec else []
            quality_note = get_value(stream, "format_note")
            youtube_format_id = get_value(stream, "format_id", convert_to=int)

            data = {
                "url": get_value(stream, "url", convert_to=[unquote, strip]),
                "codec": codec_parts[0] if codec_parts else None,
                "codecVariant": codec_parts[1] if len(codec_parts) > 1 else None,
                "rawCodec": codec,
                "extension": get_value(format_id_extension_map, youtube_format_id, default_to="mp4"),
                "width": get_value(stream, "width", convert_to=int),
                "height": get_value(stream, "height", convert_to=int),
                "framerate": get_value(stream, "fps", convert_to=float),
                "bitrate": get_value(stream, "tbr", convert_to=float),
                "qualityNote": quality_note,
                "isHDR": "hdr" in quality_note.lower() if quality_note else False,
                "size": get_value(stream, "filesize", convert_to=int),
                "language": get_value(stream, "language"),
                "youtubeFormatId": youtube_format_id,
            }

            data["quality"] = data["height"]

            return dict(sorted(data.items()))

        self.best_video_streams = (
            [extract_stream_info(stream) for stream in sorted_video_streams] if sorted_video_streams else None
        )
        self.best_video_stream = self.best_video_streams[0] if self.best_video_streams else None
        self.best_video_download_url = self.best_video_stream["url"] if self.best_video_stream else None

        self.available_video_qualities = list(
            dict.fromkeys([f"{stream['quality']}p" for stream in self.best_video_streams if stream["quality"]])
        )

        if preferred_quality != "all":
            preferred_quality = preferred_quality.strip().lower()

            if preferred_quality not in self.available_video_qualities:
                best_available_quality = max([stream["quality"] for stream in self.best_video_streams])
                self.best_video_streams = [
                    stream for stream in self.best_video_streams if stream["quality"] == best_available_quality
                ]
            else:
                self.best_video_streams = [
                    stream for stream in self.best_video_streams if stream["quality"] == int(preferred_quality.replace("p", ""))
                ]

            self.best_video_stream = self.best_video_streams[0] if self.best_video_streams else {}
            self.best_video_download_url = self.best_video_stream["url"] if self.best_video_stream else None

    def analyze_audio_streams(self, preferred_language: Union[str, Literal["source", "local", "all"]] = "local") -> None:
        """
        Analyze the audio streams of the YouTube video and select the best stream based on the preferred quality.

        Args:
            preferred_language: The preferred language for the audio stream. If 'source', use the original audio language. If 'local', use the system language. If 'all', return all available audio streams. (default: 'local')
        """

        data = self._raw_youtube_streams

        format_id_extension_map = {
            "338": "webm",  # Opus - (VBR) ~480 KBPS - Quadraphonic (4)
            "380": "mp4",  # AC3 - 384 KBPS - Surround (5.1)
            "328": "mp4",  # EAC3 - 384 KBPS - Surround (5.1)
            "325": "mp4",  # DTSE (DTS Express) - 384 KBPS - Surround (5.1)
            "258": "mp4",  # AAC (LC) - 384 KBPS - Surround (5.1)
            "327": "mp4",  # AAC (LC) - 256 KBPS - Surround (5.1)
            "141": "mp4",  # AAC (LC) - 256 KBPS - Stereo (2)
            "774": "webm",  # Opus - (VBR) ~256 KBPS - Stereo (2)
            "256": "mp4",  # AAC (HE v1) - 192 KBPS - Surround (5.1)
            "251": "webm",  # Opus - (VBR) <=160 KBPS - Stereo (2)
            "140": "mp4",  # AAC (LC) - 128 KBPS - Stereo (2)
            "250": "webm",  # Opus - (VBR) ~70 KBPS - Stereo (2)
            "249": "webm",  # Opus - (VBR) ~50 KBPS - Stereo (2)
            "139": "mp4",  # AAC (HE v1) - 48 KBPS - Stereo (2)
            "600": "webm",  # Opus - (VBR) ~35 KBPS - Stereo (2)
            "599": "mp4",  # AAC (HE v1) - 30 KBPS - Stereo (2)
        }

        audio_streams = [
            stream
            for stream in data
            if get_value(stream, "acodec") != "none"
            and get_value(stream, "format_id", "").split("-")[0] in format_id_extension_map
        ]

        def calculate_score(stream: Dict[Any, Any]) -> float:
            """
            Calculate a score for a given audio stream.

            - The score is a product of the stream's bitrate and sample rate.
            - The score is used to sort the streams in order of quality.

            Args:
                stream: The audio stream to calculate the score for. (required)

            Returns:
                The calculated score for the stream.
            """

            bitrate = get_value(stream, "abr", 0, convert_to=float)
            sample_rate = get_value(stream, "asr", 0, convert_to=float)

            bitrate_priority = 0.1  # The lower the value, the higher the priority of bitrate over samplerate

            return float((bitrate * bitrate_priority) + (sample_rate / 1000))

        sorted_audio_streams = sorted(audio_streams, key=calculate_score, reverse=True)

        def extract_stream_info(stream: Dict[Any, Any]) -> Dict[str, Optional[Union[str, int, float, bool]]]:
            """
            Extract the information of a given audio stream.

            Args:
                stream: The audio stream to extract the information from. (required)

            Returns:
                A dictionary containing the extracted information of the stream.
            """

            codec = get_value(stream, "acodec")
            codec_parts = codec.split(".", 1) if codec else []
            youtube_format_id = int(get_value(stream, "format_id", convert_to=str).split("-")[0])
            youtube_format_note = get_value(stream, "format_note")

            data = {
                "url": get_value(stream, "url", convert_to=[unquote, strip]),
                "codec": codec_parts[0] if codec_parts else None,
                "codecVariant": codec_parts[1] if len(codec_parts) > 1 else None,
                "rawCodec": codec,
                "extension": get_value(format_id_extension_map, str(youtube_format_id), "mp3"),
                "bitrate": get_value(stream, "abr", convert_to=float),
                "qualityNote": youtube_format_note,
                "isOriginalAudio": "(default)" in youtube_format_note or youtube_format_note.islower()
                if youtube_format_note
                else None,
                "size": get_value(stream, "filesize", convert_to=int),
                "samplerate": get_value(stream, "asr", convert_to=int),
                "channels": get_value(stream, "audio_channels", convert_to=int),
                "language": get_value(stream, "language"),
                "youtubeFormatId": youtube_format_id,
            }

            return dict(sorted(data.items()))

        self.best_audio_streams = (
            [extract_stream_info(stream) for stream in sorted_audio_streams] if sorted_audio_streams else None
        )
        self.best_audio_stream = self.best_audio_streams[0] if self.best_audio_streams else None
        self.best_audio_download_url = self.best_audio_stream["url"] if self.best_audio_stream else None

        self.available_audio_languages = list(
            dict.fromkeys([stream["language"].lower() for stream in self.best_audio_streams if stream["language"]])
        )

        if preferred_language != "all":
            preferred_language = preferred_language.strip().lower()

            if preferred_language == "local":
                if self.base_system_language in self.available_audio_languages:
                    self.best_audio_streams = [
                        stream for stream in self.best_audio_streams if stream["language"] == self.base_system_language
                    ]
                else:
                    preferred_language = "source"
            if preferred_language == "source":
                self.best_audio_streams = [stream for stream in self.best_audio_streams if stream["isOriginalAudio"]]
            elif preferred_language != "local":
                self.best_audio_streams = [
                    stream for stream in self.best_audio_streams if stream["language"] == preferred_language
                ]

            self.best_audio_stream = self.best_audio_streams[0] if self.best_audio_streams else {}
            self.best_audio_download_url = self.best_audio_stream["url"] if self.best_audio_stream else None

    def analyze_subtitle_streams(self) -> None:
        """
        Analyze the subtitle streams of the YouTube video.
        """

        data = self._raw_youtube_subtitles

        subtitle_streams = {}

        for stream in data:
            subtitle_streams[stream] = [
                {
                    "extension": get_value(subtitle, "ext"),
                    "url": get_value(subtitle, "url", convert_to=[unquote, strip]),
                    "language": get_value(subtitle, "name"),
                }
                for subtitle in data[stream]
            ]

        self.subtitle_streams = dict(sorted(subtitle_streams.items()))

    def download(
        self,
        video_stream: Optional[Dict[str, Any]] = None,
        audio_stream: Optional[Dict[str, Any]] = None,
        output_path: Union[str, PathLike] = Path.cwd(),
        ffmpeg_path: Union[str, PathLike, Literal["local"]] = "local",
        pre_allocate_space: bool = False,
        use_ram_buffer: bool = True,
        max_connections: Union[int, Literal["auto"]] = "auto",
        connection_speed: float = 80,
        overwrite: bool = True,
        show_progress_bar: bool = True,
        timeout: Optional[int] = None,
        logging: bool = False,
    ) -> Path:
        """
        Download the YouTube video and/or audio using the provided streams.

        - If no streams are provided, the best video and/or audio streams will be used.
        - If one stream is provided, it will be used to download the video or audio, without merging.
        - If both streams are provided, they will be merged into a single file.

        Args:
            video_stream: The video stream generated by .analyze_video_streams(). (default: None)
            audio_stream: The audio stream generated by .analyze_audio_streams(). (default: None)
            output_path: The output path to save the downloaded video and/or audio to. If a directory is provided, the file name will be generated based on the video title and ID, like 'title - [id].extension'. If a file is provided, the file will be saved with the provided name. (default: Path.cwd())
            ffmpeg_path: The path to the ffmpeg executable. If 'local', the ffmpeg executable will be searched in the PATH environment variable. (default: 'local')
            pre_allocate_space: Whether to pre-allocate space for the file, useful to avoid disk fragmentation. (default: False)
            use_ram_buffer: Whether to use a RAM buffer to download the file. (default: True)
            max_connections: The maximum number of connections to use for downloading the file. (default: 'auto')
            connection_speed: The connection speed in Mbps. (default: 80)
            overwrite: Overwrite the file if it already exists. Otherwise, a "_1", "_2", etc. suffix will be added. (default: True)
            show_progress_bar: Show or hide the download progress bar. (default: True)
            timeout: Timeout in seconds for the download process. Or None for no timeout. (default: None)
            logging: Enable or disable ffmpeg logging. (default: False)

        Returns:
            The Path object of the finished file.

        Raises:
            EmptyDataError: If no YouTube data is available. Please call .extract() first.
            InsufficientSpaceError: If there is not enough space to download the file.
        """

        if not self._raw_youtube_data:
            raise EmptyDataError("No YouTube data available. Please call .extract() first.")

        if not self.information:
            self.analyze_information(check_thumbnails=False, retrieve_dislike_count=False)

        if not video_stream and not audio_stream:
            self.analyze_video_streams(preferred_quality="all")
            self.analyze_audio_streams(preferred_language="local")

            video_stream = self.best_video_stream
            audio_stream = self.best_audio_stream

        output_path = Path(output_path)

        if video_stream and audio_stream:
            if output_path.is_dir():
                output_path = Path(
                    output_path, f"{self.information['cleanTitle']} [{self.information['id']}].{video_stream['extension']}"
                )

            tmp_path = Path(gettempdir(), ".tmp-streamsnapper-downloader")
            tmp_path.mkdir(exist_ok=True)

            output_video_path = Path(tmp_path, f".tmp-video-{self.information['id']}.{video_stream['extension']}")
            video_downloader = TurboDL(
                max_connections=max_connections,
                connection_speed=connection_speed,
                overwrite=overwrite,
                show_progress_bars=show_progress_bar,
                timeout=timeout,
            )
            video_downloader.download(
                video_stream["url"], output_video_path, pre_allocate_space=pre_allocate_space, use_ram_buffer=use_ram_buffer
            )

            output_audio_path = Path(tmp_path, f".tmp-audio-{self.information['id']}.{audio_stream['extension']}")
            audio_downloader = TurboDL(
                max_connections=max_connections,
                connection_speed=connection_speed,
                overwrite=overwrite,
                show_progress_bars=show_progress_bar,
                timeout=timeout,
            )
            audio_downloader.download(
                audio_stream["url"], output_audio_path, pre_allocate_space=pre_allocate_space, use_ram_buffer=use_ram_buffer
            )

            merger = Merger(logging=logging)
            merger.merge(
                video_path=output_video_path, audio_path=output_audio_path, output_path=output_path, ffmpeg_path=ffmpeg_path
            )

            rmtree(tmp_path)

            return output_path.resolve()
        elif video_stream:
            if output_path.is_dir():
                output_path = Path(
                    output_path, f"{self.information['cleanTitle']} [{self.information['id']}].{video_stream['extension']}"
                )

            downloader = TurboDL(
                max_connections=max_connections,
                connection_speed=connection_speed,
                overwrite=overwrite,
                show_progress_bars=show_progress_bar,
                timeout=timeout,
            )
            downloader.download(
                video_stream["url"], output_path, pre_allocate_space=pre_allocate_space, use_ram_buffer=use_ram_buffer
            )

            return Path(downloader.output_path)
        elif audio_stream:
            if output_path.is_dir():
                output_path = Path(
                    output_path, f"{self.information['cleanTitle']} [{self.information['id']}].{audio_stream['extension']}"
                )

            downloader = TurboDL(
                max_connections=max_connections,
                connection_speed=connection_speed,
                overwrite=overwrite,
                show_progress_bars=show_progress_bar,
                timeout=timeout,
            )
            downloader.download(
                audio_stream["url"], output_path, pre_allocate_space=pre_allocate_space, use_ram_buffer=use_ram_buffer
            )

            return Path(downloader.output_path)


class YouTubeExtractor:
    """
    A class for extracting data from YouTube URLs and searching for YouTube videos.
    """

    def __init__(self) -> None:
        """
        Initialize the Extractor class with some regular expressions for analyzing YouTube URLs.
        """

        self._platform_regex = re_compile(r"(?:https?://)?(?:www\.)?(music\.)?youtube\.com|youtu\.be|youtube\.com/shorts")
        self._video_id_regex = re_compile(
            r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|v/|shorts/|music/|live/|.*[?&]v=))([a-zA-Z0-9_-]{11})"
        )
        self._playlist_id_regex = re_compile(
            r"(?:youtube\.com/(?:playlist\?list=|watch\?.*?&list=|music/playlist\?list=|music\.youtube\.com/watch\?.*?&list=))([a-zA-Z0-9_-]+)"
        )

    def identify_platform(self, url: str) -> Optional[Literal["youtube", "youtubeMusic"]]:
        """
        Identify the platform of a given URL as either YouTube or YouTube Music.

        Args:
            url: The URL to identify the platform from. (required)

        Returns:
            'youtube' if the URL corresponds to YouTube, 'youtubeMusic' if it corresponds to YouTube Music. Returns None if the platform is not recognized.
        """

        found_match = self._platform_regex.search(url)

        if found_match:
            return "youtubeMusic" if found_match.group(1) else "youtube"

    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract the YouTube video ID from a URL.

        Args:
            url: The URL to extract the video ID from. (required)

        Returns:
            The extracted video ID. If no video ID is found, return None.
        """

        found_match = self._video_id_regex.search(url)

        return found_match.group(1) if found_match else None

    def extract_playlist_id(self, url: str, include_private: bool = False) -> Optional[str]:
        """
        Extract the YouTube playlist ID from a URL.

        Args:
            url: The URL to extract the playlist ID from. (required)
            include_private: Whether to include private playlists, like the mixes YouTube makes for you. (default: False)

        Returns:
            The extracted playlist ID. If no playlist ID is found or the playlist is private and include_private is False, return None.
        """

        found_match = self._playlist_id_regex.search(url)

        if found_match:
            playlist_id = found_match.group(1)

            if not include_private:
                return playlist_id if len(playlist_id) == 34 else None

            return playlist_id if len(playlist_id) >= 34 or playlist_id.startswith("RD") else None

        return None

    def search(
        self,
        query: str,
        sort_by: Literal["relevance", "upload_date", "view_count", "rating"] = "relevance",
        results_type: Literal["video", "channel", "playlist", "movie"] = "video",
        limit: int = 1,
    ) -> Optional[List[str]]:
        """
        Search for YouTube content based on a query and return a list of URLs (raw data provided by scrapetube library).

        Args:
            query: The search query string. (required)
            sort_by: The sorting method to use for the search results. Options are 'relevance', 'upload_date', 'view_count', and 'rating'. (default: 'relevance')
            results_type: The type of content to search for. Options are 'video', 'channel', 'playlist', and 'movie'. (default: 'video')
            limit: The maximum number of video URLs to return. (default: 1)

        Returns:
            A list of video URLs from the search results. If no videos are found, returns None.
        """

        try:
            extracted_data = list(
                scrape_youtube_search(query=query, sleep=1, sort_by=sort_by, results_type=results_type, limit=limit)
            )
        except Exception:
            return None

        if extracted_data:
            found_urls = [
                f"https://www.youtube.com/watch?v={item.get('videoId')}" for item in extracted_data if item.get("videoId")
            ]

            return found_urls if found_urls else None

    def get_playlist_videos(self, url: str, limit: Optional[int] = None) -> Optional[List[str]]:
        """
        Get the video URLs from a YouTube playlist (raw data provided by scrapetube library).

        Args:
            url: The URL of the YouTube playlist. (required)
            limit: The maximum number of video URLs to return. If None, return all video URLs. (default: None)

        Returns:
            A list of video URLs from the playlist. If no videos are found or the playlist is private, return None.
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
                f"https://www.youtube.com/watch?v={item.get('videoId')}" for item in extracted_data if item.get("videoId")
            ]

            return found_urls if found_urls else None

    def get_channel_videos(
        self,
        channel_id: Optional[str] = None,
        channel_url: Optional[str] = None,
        channel_username: Optional[str] = None,
        sort_by: Literal["newest", "oldest", "popular"] = "newest",
        content_type: Literal["videos", "shorts", "streams"] = "videos",
        limit: Optional[int] = None,
    ) -> Optional[List[str]]:
        """
        Get the video URLs from a YouTube channel (raw data provided by scrapetube library).

        - If channel_id, channel_url, and channel_username are all None, return None.
        - If more than one of channel_id, channel_url, and channel_username is provided, raise ValueError.

        Args:
            channel_id: The ID of the YouTube channel. (default: None)
            channel_url: The URL of the YouTube channel. (default: None)
            channel_username: The username of the YouTube channel. (default: None)
            sort_by: The sorting method to use for the channel videos. Options are 'newest', 'oldest', and 'popular' (default: 'newest').
            content_type: The type of content to search for. Options are 'videos', 'shorts', and 'streams' (default: 'videos').
            limit: The maximum number of video URLs to return. If None, return all video URLs. (default: None)

        Returns:
            A list of video URLs from the channel. If no videos are found or the channel is non-existent, return None.
        """

        if sum([bool(channel_id), bool(channel_url), bool(channel_username)]) != 1:
            raise ValueError('Provide only one of the following arguments: "channel_id", "channel_url" or "channel_username"')

        try:
            extracted_data = list(
                scrape_youtube_channel(
                    channel_id=channel_id,
                    channel_url=channel_url,
                    channel_username=channel_username.replace("@", ""),
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
                f"https://www.youtube.com/watch?v={item.get('videoId')}" for item in extracted_data if item.get("videoId")
            ]

            return found_urls if found_urls else None
