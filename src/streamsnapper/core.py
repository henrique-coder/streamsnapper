# Standard modules
from re import compile as re_compile
from typing import Any, Literal
from urllib.parse import unquote

# Third-party modules
from scrapetube import get_channel, get_playlist, get_search
from yt_dlp import YoutubeDL, utils as yt_dlp_utils
from pydantic import BaseModel

# Local modules
from .exceptions import InvalidDataError, ScrapingError
from .utils import (
    sanitize_filename,
    get_value,
    strip_whitespace,
    detect_system_language,
    filter_valid_youtube_thumbnails,
    get_youtube_dislike_count,
    SupportedCookieBrowser,
    CookieFile,
)
from .logger import logger


class VideoInformation(BaseModel):
    """Structured video information with automatic validation and serialization."""

    # URLs
    source_url: str | None = None
    short_url: str | None = None
    embed_url: str | None = None
    youtube_music_url: str | None = None
    full_url: str | None = None

    # Basic info
    id: str | None = None
    title: str | None = None
    clean_title: str | None = None
    description: str | None = None

    # Channel info
    channel_id: str | None = None
    channel_url: str | None = None
    channel_name: str | None = None
    clean_channel_name: str | None = None
    is_verified_channel: bool | None = None

    # Video stats
    duration: int | None = None
    view_count: int | None = None
    like_count: int | None = None
    dislike_count: int | None = None
    comment_count: int | None = None
    follow_count: int | None = None

    # Metadata
    is_age_restricted: bool | None = None
    categories: list[str] | None = None
    tags: list[str] | None = None
    chapters: list[dict[str, str | float]] | None = None
    is_streaming: bool | None = None
    upload_timestamp: int | None = None
    availability: str | None = None
    language: str | None = None

    # Media
    thumbnails: list[str] | None = None

    class Config:
        """Pydantic configuration."""

        validate_assignment = True
        extra = "forbid"

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""

        return self.model_dump()


class YouTube:
    """A class for extracting and formatting data from YouTube videos, facilitating access to general video information, video streams, audio streams and subtitles."""

    def __init__(self, logging: bool = False, cookies: SupportedCookieBrowser | CookieFile | None = None) -> None:
        """
        Initialize the YouTube class with the required settings for extracting and formatting data from YouTube videos (raw data provided by yt-dlp library).

        Args:
            logging: Enable or disable logging for the YouTube class. Defaults to False.
            cookies: Cookie file or browser to extract cookies from. Defaults to None.
        """

        not_logging = not logging

        if not_logging:
            logger.remove()

        logger.info("Initializing YouTube class...")

        self._ydl_opts: dict[str, bool] = {
            "extract_flat": False,
            "geo_bypass": True,
            "noplaylist": True,
            "age_limit": None,
            "ignoreerrors": True,
            "quiet": not_logging,
            "no_warnings": not_logging,
            "logger": logger,
        }

        if isinstance(cookies, SupportedCookieBrowser):
            self._ydl_opts["cookiesfrombrowser"] = (cookies.value, None, None, None)

            if logging:
                logger.info(f"Enabled cookie extraction from {cookies.value}")
        elif isinstance(cookies, CookieFile):
            self._ydl_opts["cookiefile"] = cookies.path.as_posix()

            if logging:
                logger.info(f"Enabled cookie file: {cookies.path}")
        elif cookies is not None:
            if logging:
                logger.error(f"Unsupported cookie type: {type(cookies)}")

            raise TypeError(f"Cookies must be SupportedCookieBrowser or CookieFile, got {type(cookies)}")
        else:
            if logging:
                logger.debug("Cookie extraction disabled")

        self._extractor: YouTubeExtractor = YouTubeExtractor()
        self._raw_youtube_data: dict[Any, Any] = {}
        self._raw_youtube_streams: list[dict[Any, Any]] = []
        self._raw_youtube_subtitles: dict[str, list[dict[str, str]]] = {}

        found_system_language = detect_system_language()

        self.system_language_prefix: str = found_system_language.split("-")[0]
        self.system_language_suffix: str = found_system_language.split("-")[1]

        self.information: VideoInformation = VideoInformation()

        self.best_video_streams: list[dict[str, Any]] = []
        self.best_video_stream: dict[str, Any] = {}
        self.best_video_download_url: str | None = None

        self.best_audio_streams: list[dict[str, Any]] = []
        self.best_audio_stream: dict[str, Any] = {}
        self.best_audio_download_url: str | None = None

        self.subtitle_streams: dict[str, list[dict[str, str]]] = {}

        self.available_video_qualities: list[str] = []
        self.available_audio_languages: list[str] = []

    def extract(self, url: str | None = None, ytdlp_data: dict[Any, Any] | None = None) -> None:
        """
        Extract the YouTube video data from a URL or provided previously extracted yt-dlp data.

        - If a URL is provided, it will be used to scrape the YouTube video data.
        - If yt-dlp data is provided, it will be used directly.
        - If both URL and yt-dlp data are provided, the yt-dlp data will be used.

        Args:
            url: The YouTube video URL to extract data from. Defaults to None.
            ytdlp_data: The previously extracted yt-dlp data. Defaults to None.

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
                raise ScrapingError(f'An error occurred while scraping video: "{url}" - Error: {repr(e)}') from e

        self._raw_youtube_streams = get_value(self._raw_youtube_data, "formats", convert_to=list)
        self._raw_youtube_subtitles = get_value(self._raw_youtube_data, "subtitles", convert_to=dict, default_to={})

        if self._raw_youtube_streams is None:
            raise InvalidDataError('Invalid yt-dlp data. Missing required keys: "formats"')

    def analyze_information(self, check_thumbnails: bool = False, retrieve_dislike_count: bool = False) -> None:
        """
        Analyze the information of the YouTube video.

        Args:
            check_thumbnails: Check if all video thumbnails are available. Defaults to False.
            retrieve_dislike_count: Retrieve the dislike count from the returnyoutubedislike.com API. Defaults to False.

        Raises:
            InvalidDataError: If the provided yt-dlp data is invalid.
        """

        data = self._raw_youtube_data

        id_ = get_value(data, "id")
        title = get_value(data, "fulltitle", ["title"])
        clean_title = sanitize_filename(title)
        description = get_value(data, "description")
        channel_name = get_value(data, "channel", ["uploader"])
        clean_channel_name = sanitize_filename(channel_name)
        chapters = [
            {
                "title": get_value(chapter, "title"),
                "startTime": get_value(chapter, "start_time", convert_to=float),
                "endTime": get_value(chapter, "end_time", convert_to=float),
            }
            for chapter in get_value(data, "chapters", convert_to=list, default_to=[])
        ]

        self.information.source_url = self._source_url
        self.information.short_url = f"https://youtu.be/{id_}"
        self.information.embed_url = f"https://www.youtube.com/embed/{id_}"
        self.information.youtube_music_url = f"https://music.youtube.com/watch?v={id_}"
        self.information.full_url = f"https://www.youtube.com/watch?v={id_}"
        self.information.id = id_
        self.information.title = title
        self.information.clean_title = clean_title
        self.information.description = description if description else None
        self.information.channel_id = get_value(data, "channel_id")
        self.information.channel_url = get_value(data, "channel_url", ["uploader_url"])
        self.information.channel_name = channel_name
        self.information.clean_channel_name = clean_channel_name
        self.information.is_verified_channel = get_value(data, "channel_is_verified", default_to=False)
        self.information.duration = get_value(data, "duration")
        self.information.view_count = get_value(data, "view_count")
        self.information.is_age_restricted = get_value(data, "age_limit", convert_to=bool)
        self.information.categories = get_value(data, "categories", default_to=[])
        self.information.tags = get_value(data, "tags", default_to=[])
        self.information.is_streaming = get_value(data, "is_live")
        self.information.upload_timestamp = get_value(data, "timestamp", ["release_timestamp"])
        self.information.availability = get_value(data, "availability")
        self.information.chapters = chapters
        self.information.comment_count = get_value(data, "comment_count", convert_to=int, default_to=0)
        self.information.like_count = get_value(data, "like_count", convert_to=int)
        self.information.dislike_count = None
        self.information.follow_count = get_value(data, "channel_follower_count", convert_to=int)
        self.information.language = get_value(data, "language")
        self.information.thumbnails = [
            f"https://img.youtube.com/vi/{id_}/maxresdefault.jpg",
            f"https://img.youtube.com/vi/{id_}/sddefault.jpg",
            f"https://img.youtube.com/vi/{id_}/hqdefault.jpg",
            f"https://img.youtube.com/vi/{id_}/mqdefault.jpg",
            f"https://img.youtube.com/vi/{id_}/default.jpg",
        ]

        if retrieve_dislike_count:
            logger.info(f"Retrieving dislike count for video: {id_}")
            dislike_count = get_youtube_dislike_count(id_)

            if dislike_count is not None:
                self.information.dislike_count = dislike_count
                logger.info(f"Retrieved dislike count for video: {id_}: {dislike_count}")
            else:
                logger.warning(f"Failed to retrieve dislike count for video: {id_}")

        if check_thumbnails:
            self.information.thumbnails = filter_valid_youtube_thumbnails(self.information.thumbnails)
            logger.info(f"Filtered valid thumbnails for video: {id_}: {self.information.thumbnails}")

    def analyze_video_streams(
        self,
        preferred_quality: Literal["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "4320p", "all"] = "all",
    ) -> None:
        """
        Analyze the video streams of the YouTube video and select the best stream based on the preferred quality.

        Args:
            preferred_quality: The preferred quality of the video stream. If a specific quality is provided, the stream will be selected according to the chosen quality, however if the quality is not available, the best quality will be selected. If 'all', all streams will be considered and sorted by quality. Defaults to 'all'.
        """

        data = self._raw_youtube_streams

        # Video format ID extension map
        format_id_extension_map = {
            702: "mp4",  # AV1 HFR High - MP4 - 7680x4320
            402: "mp4",  # AV1 HFR - MP4 - 7680x4320
            571: "mp4",  # AV1 HFR - MP4 - 7680x4320
            272: "webm",  # VP9 HFR - WebM - 7680x4320
            138: "mp4",  # H.264 - MP4 - 7680x4320
            701: "mp4",  # AV1 HFR High - MP4 - 3840x2160
            401: "mp4",  # AV1 HFR - MP4 - 3840x2160
            337: "webm",  # VP9.2 HDR HFR - WebM - 3840x2160
            315: "webm",  # VP9 HFR - WebM - 3840x2160
            313: "webm",  # VP9 - WebM - 3840x2160
            305: "mp4",  # H.264 HFR - MP4 - 3840x2160
            266: "mp4",  # H.264 - MP4 - 3840x2160
            700: "mp4",  # AV1 HFR High - MP4 - 2560x1440
            400: "mp4",  # AV1 HFR - MP4 - 2560x1440
            336: "webm",  # VP9.2 HDR HFR - WebM - 2560x1440
            308: "webm",  # VP9 HFR - WebM - 2560x1440
            271: "webm",  # VP9 - WebM - 2560x1440
            304: "mp4",  # H.264 HFR - MP4 - 2560x1440
            264: "mp4",  # H.264 - MP4 - 2560x1440
            699: "mp4",  # AV1 HFR High - MP4 - 1920x1080
            399: "mp4",  # AV1 HFR - MP4 - 1920x1080
            721: "mp4",  # AV1 HFR - MP4 - 1920x1080
            335: "webm",  # VP9.2 HDR HFR - WebM - 1920x1080
            303: "webm",  # VP9 HFR - WebM - 1920x1080
            248: "webm",  # VP9 - WebM - 1920x1080
            # 616: "webm",  # VP9 - WebM - 1920x1080 - YouTube Premium Format (M3U8)
            299: "mp4",  # H.264 HFR - MP4 - 1920x1080
            137: "mp4",  # H.264 - MP4 - 1920x1080
            216: "mp4",  # H.264 - MP4 - 1920x1080
            170: "webm",  # VP8 - WebM - 1920x1080
            698: "mp4",  # AV1 HFR High - MP4 - 1280x720
            398: "mp4",  # AV1 HFR - MP4 - 1280x720
            334: "webm",  # VP9.2 HDR HFR - WebM - 1280x720
            302: "webm",  # VP9 HFR - WebM - 1280x720
            612: "webm",  # VP9 HFR - WebM - 1280x720
            247: "webm",  # VP9 - WebM - 1280x720
            298: "mp4",  # H.264 HFR - MP4 - 1280x720
            136: "mp4",  # H.264 - MP4 - 1280x720
            169: "webm",  # VP8 - WebM - 1280x720
            697: "mp4",  # AV1 HFR High - MP4 - 854x480
            397: "mp4",  # AV1 - MP4 - 854x480
            333: "webm",  # VP9.2 HDR HFR - WebM - 854x480
            244: "webm",  # VP9 - WebM - 854x480
            135: "mp4",  # H.264 - MP4 - 854x480
            168: "webm",  # VP8 - WebM - 854x480
            696: "mp4",  # AV1 HFR High - MP4 - 640x360
            396: "mp4",  # AV1 - MP4 - 640x360
            332: "webm",  # VP9.2 HDR HFR - WebM - 640x360
            243: "webm",  # VP9 - WebM - 640x360
            134: "mp4",  # H.264 - MP4 - 640x360
            167: "webm",  # VP8 - WebM - 640x360
            695: "mp4",  # AV1 HFR High - MP4 - 426x240
            395: "mp4",  # AV1 - MP4 - 426x240
            331: "webm",  # VP9.2 HDR HFR - WebM - 426x240
            242: "webm",  # VP9 - WebM - 426x240
            133: "mp4",  # H.264 - MP4 - 426x240
            694: "mp4",  # AV1 HFR High - MP4 - 256x144
            394: "mp4",  # AV1 - MP4 - 256x144
            330: "webm",  # VP9.2 HDR HFR - WebM - 256x144
            278: "webm",  # VP9 - WebM - 256x144
            598: "webm",  # VP9 - WebM - 256x144
            160: "mp4",  # H.264 - MP4 - 256x144
            597: "mp4",  # H.264 - MP4 - 256x144
        }

        video_streams = [
            stream
            for stream in data
            if get_value(stream, "vcodec") != "none" and get_value(stream, "format_id", convert_to=int) in format_id_extension_map
        ]

        def calculate_score(stream: dict[Any, Any]) -> float:
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

        def extract_stream_info(stream: dict[Any, Any]) -> dict[str, str | int | float | bool | None]:
            """
            Extract the information of a given video stream.

            Args:
                stream: The video stream to extract the information from.

            Returns:
                A dictionary containing the extracted information of the stream.
            """

            codec = get_value(stream, "vcodec")
            codec_parts = codec.split(".", 1) if codec else []
            quality_note = get_value(stream, "format_note")
            youtube_format_id = get_value(stream, "format_id", convert_to=int)

            data = {
                "url": get_value(stream, "url", convert_to=[unquote, strip_whitespace]),
                "codec": codec_parts[0] if codec_parts else None,
                "codec_variant": codec_parts[1] if len(codec_parts) > 1 else None,
                "raw_codec": codec,
                "extension": get_value(format_id_extension_map, youtube_format_id, default_to="mp4"),
                "width": get_value(stream, "width", convert_to=int),
                "height": get_value(stream, "height", convert_to=int),
                "framerate": get_value(stream, "fps", convert_to=float),
                "bitrate": get_value(stream, "tbr", convert_to=float),
                "quality_note": quality_note,
                "is_hdr": "hdr" in quality_note.lower() if quality_note else False,
                "size": get_value(stream, "filesize", convert_to=int),
                "language": get_value(stream, "language"),
                "youtube_format_id": youtube_format_id,
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

    def analyze_audio_streams(self, preferred_language: str | Literal["source", "local", "all"] = "source") -> None:
        """
        Analyze the audio streams of the YouTube video and select the best stream based on the preferred quality.

        Args:
            preferred_language: The preferred language for the audio stream. If 'source', use the original audio language. If 'local', use the system language. If 'all', return all available audio streams. Or a specific language code in format 'en-US'. Defaults to 'source'.
        """

        data = self._raw_youtube_streams

        # Audio format ID extension map
        format_id_extension_map = {
            "773": "mp4",  # IAMF (Opus) - (VBR) ~900 KBPS - Binaural (7.1.4)
            "338": "webm",  # Opus - (VBR) ~480 KBPS (?) - Ambisonic (4)
            "380": "mp4",  # AC3 - 384 KBPS - Surround (5.1)
            "328": "mp4",  # EAC3 - 384 KBPS - Surround (5.1)
            "325": "mp4",  # DTSE (DTS Express) - 384 KBPS - Surround (5.1)
            "258": "mp4",  # AAC (LC) - 384 KBPS - Surround (5.1)
            "327": "mp4",  # AAC (LC) - 256 KBPS - Surround (5.1)
            "141": "mp4",  # AAC (LC) - 256 KBPS - Stereo (2)
            "774": "webm",  # Opus - (VBR) ~256 KBPS - Stereo (2)
            "256": "mp4",  # AAC (HE v1) - 192 KBPS - Surround (5.1)
            "251": "webm",  # Opus - (VBR) ~128 KBPS - Stereo (2)
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

        def calculate_score(stream: dict[Any, Any]) -> float:
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

        def extract_stream_info(stream: dict[Any, Any]) -> dict[str, str | int | float | bool | None]:
            """
            Extract the information of a given audio stream.

            Args:
                stream: The audio stream to extract the information from.

            Returns:
                A dictionary containing the extracted information of the stream.
            """

            codec = get_value(stream, "acodec")
            codec_parts = codec.split(".", 1) if codec else []
            youtube_format_id = int(get_value(stream, "format_id", convert_to=str).split("-")[0])
            youtube_format_note = get_value(stream, "format_note")

            data = {
                "url": get_value(stream, "url", convert_to=[unquote, strip_whitespace]),
                "codec": codec_parts[0] if codec_parts else None,
                "codec_variant": codec_parts[1] if len(codec_parts) > 1 else None,
                "raw_codec": codec,
                "extension": get_value(format_id_extension_map, str(youtube_format_id), "mp3"),
                "bitrate": get_value(stream, "abr", convert_to=float),
                "quality_note": youtube_format_note,
                "is_original_audio": "(default)" in youtube_format_note or youtube_format_note.islower()
                if youtube_format_note
                else None,
                "size": get_value(stream, "filesize", convert_to=int),
                "samplerate": get_value(stream, "asr", convert_to=int),
                "channels": get_value(stream, "audio_channels", convert_to=int),
                "language": get_value(stream, "language"),
                "youtube_format_id": youtube_format_id,
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
                if self.system_language_prefix in self.available_audio_languages:
                    self.best_audio_streams = [
                        stream for stream in self.best_audio_streams if stream["language"] == self.system_language_prefix
                    ]
                else:
                    preferred_language = "source"
            if preferred_language == "source":
                self.best_audio_streams = [stream for stream in self.best_audio_streams if stream["is_original_audio"]]
            elif preferred_language != "local":
                self.best_audio_streams = [
                    stream for stream in self.best_audio_streams if stream["language"] == preferred_language
                ]

            self.best_audio_stream = self.best_audio_streams[0] if self.best_audio_streams else {}
            self.best_audio_download_url = self.best_audio_stream["url"] if self.best_audio_stream else None

    def analyze_subtitle_streams(self) -> None:
        """Analyze the subtitle streams of the YouTube video."""

        data = self._raw_youtube_subtitles

        subtitle_streams = {}

        for stream in data:
            subtitle_streams[stream] = [
                {
                    "extension": get_value(subtitle, "ext"),
                    "url": get_value(subtitle, "url", convert_to=[unquote, strip_whitespace]),
                    "language": get_value(subtitle, "name"),
                }
                for subtitle in data[stream]
            ]

        self.subtitle_streams = dict(sorted(subtitle_streams.items()))


class YouTubeExtractor:
    """A class for extracting data from YouTube URLs and searching for YouTube videos."""

    def __init__(self) -> None:
        """Initialize the Extractor class with some regular expressions for analyzing YouTube URLs."""

        self._platform_regex = re_compile(r"(?:https?://)?(?:www\.)?(music\.)?youtube\.com|youtu\.be|youtube\.com/shorts")
        self._video_id_regex = re_compile(
            r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|v/|shorts/|music/|live/|.*[?&]v=))([a-zA-Z0-9_-]{11})"
        )
        self._playlist_id_regex = re_compile(
            r"(?:youtube\.com/(?:playlist\?list=|watch\?.*?&list=|music/playlist\?list=|music\.youtube\.com/watch\?.*?&list=))([a-zA-Z0-9_-]+)"
        )

    def identify_platform(self, url: str) -> Literal["youtube", "youtubeMusic"] | None:
        """
        Identify the platform of a given URL as either YouTube or YouTube Music.

        Args:
            url: The URL to identify the platform from.

        Returns:
            'youtube' if the URL corresponds to YouTube, 'youtubeMusic' if it corresponds to YouTube Music. Returns None if the platform is not recognized.
        """

        found_match = self._platform_regex.search(url)

        if found_match:
            return "youtubeMusic" if found_match.group(1) else "youtube"

    def extract_video_id(self, url: str) -> str | None:
        """
        Extract the YouTube video ID from a URL.

        Args:
            url: The URL to extract the video ID from.

        Returns:
            The extracted video ID. If no video ID is found, return None.
        """

        found_match = self._video_id_regex.search(url)

        return found_match.group(1) if found_match else None

    def extract_playlist_id(self, url: str, include_private: bool = False) -> str | None:
        """
        Extract the YouTube playlist ID from a URL.

        Args:
            url: The URL to extract the playlist ID from.
            include_private: Whether to include private playlists, like the mixes YouTube makes for you. Defaults to False.

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
    ) -> list[dict[str, str]] | None:
        """
        Search for YouTube content based on a query and return a list of URLs (raw data provided by scrapetube library).

        Args:
            query: The search query string.
            sort_by: The sorting method to use for the search results. Options are 'relevance', 'upload_date', 'view_count', and 'rating'. Defaults to 'relevance'.
            results_type: The type of content to search for. Options are 'video', 'channel', 'playlist', and 'movie'. Defaults to 'video'.
            limit: The maximum number of video URLs to return. Defaults to 1.

        Returns:
            A list of dictionaries containing information about the found videos. If no videos are found, return None.
        """

        try:
            extracted_data = list(get_search(query=query, sleep=1, sort_by=sort_by, results_type=results_type, limit=limit))
        except Exception:
            return None

        if extracted_data:
            return extracted_data

        return None

    def get_playlist_videos(self, url: str, limit: int | None = None) -> list[str] | None:
        """
        Get the video URLs from a YouTube playlist (raw data provided by scrapetube library).

        Args:
            url: The URL of the YouTube playlist.
            limit: The maximum number of video URLs to return. If None, return all video URLs. Defaults to None.

        Returns:
            A list of video URLs from the playlist. If no videos are found or the playlist is private, return None.
        """

        playlist_id = self.extract_playlist_id(url, include_private=False)

        if not playlist_id:
            return None

        try:
            extracted_data = list(get_playlist(playlist_id, sleep=1, limit=limit))
        except Exception:
            return None

        if extracted_data:
            found_urls = [
                f"https://www.youtube.com/watch?v={item.get('videoId')}" for item in extracted_data if item.get("videoId")
            ]

            return found_urls if found_urls else None

    def get_channel_videos(
        self,
        channel_id: str | None = None,
        channel_url: str | None = None,
        channel_username: str | None = None,
        sort_by: Literal["newest", "oldest", "popular"] = "newest",
        content_type: Literal["videos", "shorts", "streams"] = "videos",
        limit: int | None = None,
    ) -> list[str] | None:
        """
        Get the video URLs from a YouTube channel (raw data provided by scrapetube library).

        - If channel_id, channel_url, and channel_username are all None, return None.
        - If more than one of channel_id, channel_url, and channel_username is provided, raise ValueError.

        Args:
            channel_id: The ID of the YouTube channel. Defaults to None.
            channel_url: The URL of the YouTube channel. Defaults to None.
            channel_username: The username of the YouTube channel. Defaults to None.
            sort_by: The sorting method to use for the channel videos. Options are 'newest', 'oldest', and 'popular'. Defaults to 'newest'.
            content_type: The type of content to search for. Options are 'videos', 'shorts', and 'streams'. Defaults to 'videos'.
            limit: The maximum number of video URLs to return. If None, return all video URLs. Defaults to None.

        Returns:
            A list of video URLs from the channel. If no videos are found or the channel is non-existent, return None.
        """

        if sum([bool(channel_id), bool(channel_url), bool(channel_username)]) != 1:
            raise ValueError('Provide only one of the following arguments: "channel_id", "channel_url" or "channel_username"')

        try:
            extracted_data = list(
                get_channel(
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
