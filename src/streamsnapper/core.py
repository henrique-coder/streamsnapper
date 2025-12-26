from re import compile as re_compile
from typing import Any, Literal
from urllib.parse import unquote

from yt_dlp import YoutubeDL
from yt_dlp import utils as yt_dlp_utils

from .exceptions import InvalidDataError, ScrapingError
from .logger import logger
from .models import (
    AudioStream,
    AudioStreamCollection,
    SubtitleStream,
    SubtitleStreamCollection,
    VideoInformation,
    VideoStream,
    VideoStreamCollection,
)
from .utils import (
    CookieFile,
    SupportedCookieBrowser,
    detect_system_language,
    filter_valid_youtube_thumbnails,
    get_value,
    get_youtube_dislike_count,
    sanitize_filename,
    strip_whitespace,
)


class YouTube:
    """
    YouTube video extractor with stream analysis and metadata retrieval.

    Extracts video/audio streams, metadata, and subtitles with intelligent
    quality and language selection.
    """

    def __init__(self, logging: bool = False, cookies: SupportedCookieBrowser | CookieFile | None = None) -> None:
        """
        Initialize the YouTube extractor.

        Args:
            logging: Enable detailed logging. Defaults to False.
            cookies: Cookie source for accessing restricted content. Defaults to None.
        """

        not_logging = not logging

        if not_logging:
            logger.remove()

        logger.info("Initializing YouTube class...")

        self._ydl_opts: dict[str, Any] = {
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
        elif logging:
            logger.debug("Cookie extraction disabled")

        self._extractor: YouTubeExtractor = YouTubeExtractor()
        self._raw_youtube_data: dict[Any, Any] = {}
        self._raw_youtube_streams: list[dict[Any, Any]] = []
        self._raw_youtube_subtitles: dict[str, list[dict[str, str]]] = {}

        found_system_language = detect_system_language().split("-")

        self.system_language_prefix: str = found_system_language[0]
        self.system_language_suffix: str = found_system_language[1]

        # Initialize data models
        self.information: VideoInformation = VideoInformation()
        self.video_streams: VideoStreamCollection = VideoStreamCollection()
        self.audio_streams: AudioStreamCollection = AudioStreamCollection()
        self.subtitle_streams: SubtitleStreamCollection = SubtitleStreamCollection()

    def extract(self, url: str) -> None:
        """
        Extract YouTube video data from URL.

        Args:
            url: YouTube video URL.

        Raises:
            ValueError: If URL is invalid.
            ScrapingError: If extraction fails.
        """

        self._source_url = url

        if not url:
            raise ValueError("No YouTube video URL provided")

        video_id = self._extractor.extract_video_id(url)

        if not video_id:
            raise ValueError(f'Invalid YouTube video URL: "{url}"')

        try:
            with YoutubeDL(self._ydl_opts) as ydl:
                self._raw_youtube_data = ydl.extract_info(url=url, download=False, process=True)
        except (yt_dlp_utils.DownloadError, yt_dlp_utils.ExtractorError, Exception) as e:
            raise ScrapingError(f'An error occurred while scraping video: "{url}" - Error: {e!r}') from e

        self._raw_youtube_streams = get_value(self._raw_youtube_data, "formats", convert_to=list)
        self._raw_youtube_subtitles = get_value(self._raw_youtube_data, "subtitles", convert_to=dict, default_to={})

        if self._raw_youtube_streams is None:
            raise InvalidDataError('Invalid yt-dlp data. Missing required keys: "formats"')

    def analyze_information(self, check_thumbnails: bool = False, retrieve_dislike_count: bool = False) -> None:
        """
        Analyze video metadata and statistics.

        Args:
            check_thumbnails: Validate thumbnail URLs. Defaults to False.
            retrieve_dislike_count: Fetch dislikes from external API. Defaults to False.

        Raises:
            InvalidDataError: If data extraction fails.
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

        # URL generation
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
        preferred_resolution: Literal[
            "144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "4320p", "worst", "best", "all"
        ] = "all",
        fallback: bool = True,
    ) -> None:
        """
        Analyze and filter video streams by resolution.

        Args:
            preferred_resolution: Target resolution or selection mode. Defaults to "all".
            fallback: Enable lower resolution fallback. Defaults to True.
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
            # 356: "webm",  # VP9 - WebM - 1920x1080 - YouTube Premium Format (M3U8)
            299: "mp4",  # H.264 HFR - MP4 - 1920x1080
            137: "mp4",  # H.264 - MP4 - 1920x1080
            170: "webm",  # VP8 - WebM - 1920x1080
            698: "mp4",  # AV1 HFR High - MP4 - 1280x720
            398: "mp4",  # AV1 HFR - MP4 - 1280x720
            334: "webm",  # VP9.2 HDR HFR - WebM - 1280x720
            302: "webm",  # VP9 HFR - WebM - 1280x720
            612: "webm",  # VP9 HFR - WebM - 1280x720
            247: "webm",  # VP9 - WebM - 1280x720
            298: "mp4",  # H.264 HFR - MP4 - 1280x720
            136: "mp4",  # H.264 - MP4 - 1280x720
            214: "mp4",  # H.264 - MP4 - 1280x720
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
            if get_value(stream, "vcodec") != "none"
            and get_value(stream, "format_id", convert_to=int) in format_id_extension_map
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

            width = get_value(stream, "width", default_to=0, convert_to=int)
            height = get_value(stream, "height", default_to=0, convert_to=int)
            framerate = get_value(stream, "fps", default_to=0, convert_to=float)
            bitrate = get_value(stream, "tbr", default_to=0, convert_to=float)

            return float(width * height * framerate * bitrate)

        sorted_video_streams = sorted(video_streams, key=calculate_score, reverse=True)

        def extract_stream_info(stream: dict[Any, Any]) -> VideoStream:
            """
            Extract the information of a given video stream and create a VideoStream model.

            Args:
                stream: The video stream to extract the information from.

            Returns:
                A VideoStream model with the extracted information.
            """

            codec = get_value(stream, "vcodec")
            codec_parts = codec.split(".", 1) if codec else []
            quality_note = get_value(stream, "format_note")
            youtube_format_id = get_value(stream, "format_id", convert_to=int)

            return VideoStream(
                url=get_value(stream, "url", convert_to=[unquote, strip_whitespace]),
                codec=codec_parts[0] if codec_parts else None,
                codec_variant=codec_parts[1] if len(codec_parts) > 1 else None,
                raw_codec=codec,
                extension=get_value(format_id_extension_map, youtube_format_id, default_to="mp4"),
                width=get_value(stream, "width", convert_to=int),
                height=get_value(stream, "height", convert_to=int),
                framerate=get_value(stream, "fps", convert_to=float),
                bitrate=get_value(stream, "tbr", convert_to=float),
                quality_note=quality_note,
                is_hdr="hdr" in quality_note.lower() if quality_note else False,
                size=get_value(stream, "filesize", convert_to=int),
                language=get_value(stream, "language"),
                youtube_format_id=youtube_format_id,
            )

        # Create Pydantic models
        if sorted_video_streams:
            video_stream_models = [extract_stream_info(stream) for stream in sorted_video_streams]
            self.video_streams = VideoStreamCollection(streams=video_stream_models)
        else:
            self.video_streams = VideoStreamCollection()

        if preferred_resolution != "all":
            resolution = preferred_resolution.strip().lower()

            if resolution == "best":
                logger.debug("Selecting best available video resolution")
                best_stream = self.video_streams.best_stream
                if best_stream:
                    self.video_streams = VideoStreamCollection(streams=[best_stream])
            elif resolution == "worst":
                logger.debug("Selecting worst available video resolution")
                worst_stream = self.video_streams.worst_stream
                if worst_stream:
                    self.video_streams = VideoStreamCollection(streams=[worst_stream])
            else:
                target_resolution = resolution
                logger.debug(
                    f"Target resolution: {target_resolution}, available: {self.video_streams.available_qualities}"
                )

                filtered_streams = self.video_streams.get_by_resolution(target_resolution, fallback=fallback)
                if filtered_streams:
                    logger.debug(f"Found {len(filtered_streams)} streams for resolution {target_resolution}")
                    self.video_streams = VideoStreamCollection(streams=filtered_streams)
                else:
                    logger.debug(f"No streams found for resolution {target_resolution}")
                    self.video_streams = VideoStreamCollection()

    def analyze_audio_streams(self, preferred_language: str | list[str] = "all") -> None:
        """
        Analyze and filter audio streams by language preference.

        Args:
            preferred_language: Language selection strategy. String for single language,
                list for priority fallback, "local" for system language, "source" for
                original audio, "all" for all streams. Defaults to "all".
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
            and get_value(stream, "format_id", default_to="").split("-")[0] in format_id_extension_map
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

            bitrate = get_value(stream, "abr", default_to=0, convert_to=float)
            sample_rate = get_value(stream, "asr", default_to=0, convert_to=float)

            bitrate_priority = 0.1  # The lower the value, the higher the priority of bitrate over sample rate

            return float((bitrate * bitrate_priority) + (sample_rate / 1000))

        sorted_audio_streams = sorted(audio_streams, key=calculate_score, reverse=True)

        def extract_stream_info(stream: dict[Any, Any]) -> AudioStream:
            """
            Extract the information of a given audio stream and create an AudioStream model.

            Args:
                stream: The audio stream to extract the information from.

            Returns:
                An AudioStream model with the extracted information.
            """

            codec = get_value(stream, "acodec")
            codec_parts = codec.split(".", 1) if codec else []
            youtube_format_id = int(get_value(stream, "format_id", convert_to=str).split("-")[0])

            # Determine language name - this would need language mapping logic
            language_code = get_value(stream, "language")
            language_name = None  # Could be enhanced with language code to name mapping

            return AudioStream(
                url=get_value(stream, "url", convert_to=[unquote, strip_whitespace]),
                codec=codec_parts[0] if codec_parts else None,
                codec_variant=codec_parts[1] if len(codec_parts) > 1 else None,
                raw_codec=codec,
                extension=get_value(format_id_extension_map, str(youtube_format_id), default_to="mp3"),
                bitrate=get_value(stream, "abr", convert_to=float),
                sample_rate=get_value(stream, "asr", convert_to=int),
                channels=get_value(stream, "audio_channels", convert_to=int),
                language=language_code,
                language_name=language_name,
                size=get_value(stream, "filesize", convert_to=int),
                youtube_format_id=youtube_format_id,
            )

        # Create Pydantic models
        if sorted_audio_streams:
            audio_stream_models = [extract_stream_info(stream) for stream in sorted_audio_streams]
            self.audio_streams = AudioStreamCollection(streams=audio_stream_models)
        else:
            self.audio_streams = AudioStreamCollection()

        # Language filtering using preference list with source fallback
        if preferred_language != "all":
            language_list = [preferred_language] if isinstance(preferred_language, str) else preferred_language

            filtered_streams = []

            # Try each language preference in order
            for lang in language_list:
                if lang == "source":
                    best = self.audio_streams.best_stream
                    if best:
                        filtered_streams = [best]
                        break
                elif lang == "local":
                    system_lang = f"{self.system_language_prefix}-{self.system_language_suffix}"
                    for fallback_lang in [system_lang, self.system_language_prefix]:
                        filtered_streams = self.audio_streams.get_by_language(fallback_lang, fallback=False)
                        if filtered_streams:
                            break
                    if filtered_streams:
                        break
                else:
                    # Try specific language
                    filtered_streams = self.audio_streams.get_by_language(lang, fallback=True)
                    if filtered_streams:
                        break

            if not filtered_streams:
                best = self.audio_streams.best_stream
                if best:
                    logger.debug("No language match found, falling back to best quality")
                    filtered_streams = [best]

            if filtered_streams:
                self.audio_streams = AudioStreamCollection(streams=filtered_streams)

    def analyze_subtitle_streams(self) -> None:
        """Analyze and extract subtitle stream information."""

        data = self._raw_youtube_subtitles

        subtitle_stream_models = []

        for language_code, subtitle_list in data.items():
            for subtitle in subtitle_list:
                try:
                    subtitle_stream = SubtitleStream(
                        url=get_value(subtitle, "url", convert_to=[unquote, strip_whitespace]),
                        extension=get_value(subtitle, "ext", default_to="srt"),
                        language=language_code,
                        language_name=get_value(subtitle, "name"),
                        is_auto_generated=False,  # Would need logic to detect this
                        is_translatable=False,  # Would need logic to detect this
                        is_fragment_based=False,  # Would need logic to detect this
                        youtube_format_id=get_value(subtitle, "format_id"),
                    )
                    subtitle_stream_models.append(subtitle_stream)
                except Exception as e:  # noqa: PERF203
                    logger.warning(f"Failed to create subtitle stream for {language_code}: {e}")
                    continue

        self.subtitle_streams = SubtitleStreamCollection(streams=subtitle_stream_models)


class YouTubeExtractor:
    """
    URL analyzer and ID extractor for YouTube content.

    Provides utilities for extracting video/playlist IDs and platform detection.
    """

    def __init__(self) -> None:
        """Initialize the extractor with regex patterns for YouTube URL analysis."""

        self._platform_regex = re_compile(
            r"(?:https?://)?(?:www\.)?(music\.)?youtube\.com|youtu\.be|youtube\.com/shorts"
        )
        self._video_id_regex = re_compile(
            r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/|v/|shorts/|music/|live/|.*[?&]v=))([a-zA-Z0-9_-]{11})"
        )
        self._playlist_id_regex = re_compile(
            r"(?:youtube\.com/(?:playlist\?list=|watch\?.*?&list=|music/playlist\?list=|music\.youtube\.com/watch\?.*?&list=))([a-zA-Z0-9_-]+)"
        )

    def identify_platform(self, url: str) -> Literal["youtube", "youtube_music"] | None:
        """
        Identify the platform of a given URL as either YouTube or YouTube Music.

        Args:
            url: The URL to identify the platform from.

        Returns:
            'youtube' if the URL corresponds to YouTube, 'youtube_music'
            if it corresponds to YouTube Music. Returns None if the platform is not recognized.
        """

        found_match = self._platform_regex.search(url)

        if found_match:
            return "youtube_music" if found_match.group(1) else "youtube"

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
            include_private: Whether to include private playlists, like the mixes
                YouTube makes for you. Defaults to False.

        Returns:
            The extracted playlist ID. If no playlist ID is found or the playlist
            is private and include_private is False, return None.
        """

        found_match = self._playlist_id_regex.search(url)

        if found_match:
            playlist_id = found_match.group(1)

            if not include_private:
                return playlist_id if len(playlist_id) == 34 else None

            return playlist_id if len(playlist_id) >= 34 or playlist_id.startswith("RD") else None

        return None
