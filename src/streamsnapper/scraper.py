"""YouTube data extraction and processing utilities."""

from typing import Any
from urllib.parse import unquote

from yt_dlp import YoutubeDL
from yt_dlp import utils as yt_dlp_utils

from .data import AUDIO_FORMAT_EXTENSIONS, QUALITY_WEIGHTS, VIDEO_FORMAT_EXTENSIONS
from .exceptions import ScrapingError
from .utils import get_value, strip_whitespace


class YouTubeExtractor:
    """High-performance YouTube data extractor using yt-dlp."""

    def __init__(self, ydl_opts: dict[str, Any] | None = None):
        """Initialize extractor with optional yt-dlp options."""
        self.ydl_opts = ydl_opts or {}

    def extract_data(self, url: str) -> dict[str, Any]:
        """Extract raw data from YouTube URL."""
        try:
            with YoutubeDL(self.ydl_opts) as ydl:
                return ydl.extract_info(url=url, download=False, process=True)
        except (yt_dlp_utils.DownloadError, yt_dlp_utils.ExtractorError, Exception) as e:
            raise ScrapingError(f'Failed to extract data from "{url}": {e}') from e

    def extract_video_streams(self, raw_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract and filter video streams from raw data."""
        formats = get_value(raw_data, "formats", convert_to=list, default_to=[])

        return [
            stream
            for stream in formats
            if (
                get_value(stream, "vcodec") != "none"
                and get_value(stream, "format_id", convert_to=int) in VIDEO_FORMAT_EXTENSIONS
            )
        ]

    def extract_audio_streams(self, raw_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract and filter audio streams from raw data."""
        formats = get_value(raw_data, "formats", convert_to=list, default_to=[])

        return [
            stream
            for stream in formats
            if (
                get_value(stream, "acodec") != "none"
                and get_value(stream, "format_id", "").split("-")[0] in AUDIO_FORMAT_EXTENSIONS
            )
        ]

    def extract_subtitle_streams(self, raw_data: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
        """Extract subtitle streams from raw data."""
        return get_value(raw_data, "subtitles", convert_to=dict, default_to={})


class StreamProcessor:
    """Process and score streams for quality ranking."""

    @staticmethod
    def calculate_video_score(stream: dict[str, Any]) -> float:
        """Calculate quality score for video stream."""
        width = get_value(stream, "width", 0, convert_to=int)
        height = get_value(stream, "height", 0, convert_to=int)
        framerate = get_value(stream, "fps", 0, convert_to=float)
        bitrate = get_value(stream, "tbr", 0, convert_to=float)

        return float(
            (width * QUALITY_WEIGHTS["width"])
            * (height * QUALITY_WEIGHTS["height"])
            * (framerate * QUALITY_WEIGHTS["framerate"])
            * (bitrate * QUALITY_WEIGHTS["bitrate"])
        )

    @staticmethod
    def calculate_audio_score(stream: dict[str, Any]) -> float:
        """Calculate quality score for audio stream."""
        bitrate = get_value(stream, "abr", 0, convert_to=float)
        sample_rate = get_value(stream, "asr", 0, convert_to=float)

        return float((bitrate * QUALITY_WEIGHTS["bitrate"]) + (sample_rate * QUALITY_WEIGHTS["sample_rate"]))

    @staticmethod
    def sort_streams_by_quality(streams: list[dict[str, Any]], stream_type: str) -> list[dict[str, Any]]:
        """Sort streams by quality score."""
        if stream_type == "video":
            return sorted(streams, key=StreamProcessor.calculate_video_score, reverse=True)
        elif stream_type == "audio":
            return sorted(streams, key=StreamProcessor.calculate_audio_score, reverse=True)
        else:
            return streams


class StreamConverter:
    """Convert raw stream data to standardized format."""

    @staticmethod
    def convert_video_stream(stream: dict[str, Any]) -> dict[str, Any]:
        """Convert raw video stream to clean format."""
        codec = get_value(stream, "vcodec")
        codec_parts = codec.split(".", 1) if codec else []
        quality_note = get_value(stream, "format_note")
        format_id = get_value(stream, "format_id", convert_to=int)

        return {
            "url": get_value(stream, "url", convert_to=[unquote, strip_whitespace]),
            "codec": codec_parts[0] if codec_parts else None,
            "codec_variant": codec_parts[1] if len(codec_parts) > 1 else None,
            "raw_codec": codec,
            "extension": VIDEO_FORMAT_EXTENSIONS.get(format_id, "mp4"),
            "width": get_value(stream, "width", convert_to=int),
            "height": get_value(stream, "height", convert_to=int),
            "framerate": get_value(stream, "fps", convert_to=float),
            "bitrate": get_value(stream, "tbr", convert_to=float),
            "quality_note": quality_note,
            "is_hdr": "hdr" in quality_note.lower() if quality_note else False,
            "size": get_value(stream, "filesize", convert_to=int),
            "language": get_value(stream, "language"),
            "youtube_format_id": format_id,
        }

    @staticmethod
    def convert_audio_stream(stream: dict[str, Any]) -> dict[str, Any]:
        """Convert raw audio stream to clean format."""
        codec = get_value(stream, "acodec")
        codec_parts = codec.split(".", 1) if codec else []
        format_id_str = get_value(stream, "format_id", convert_to=str, default_to="251")
        format_id = format_id_str.split("-")[0] if format_id_str else "251"

        return {
            "url": get_value(stream, "url", convert_to=[unquote, strip_whitespace]),
            "codec": codec_parts[0] if codec_parts else None,
            "codec_variant": codec_parts[1] if len(codec_parts) > 1 else None,
            "raw_codec": codec,
            "extension": AUDIO_FORMAT_EXTENSIONS.get(format_id, "mp3"),
            "bitrate": get_value(stream, "abr", convert_to=float),
            "sample_rate": get_value(stream, "asr", convert_to=int),
            "channels": get_value(stream, "audio_channels", convert_to=int),
            "language": get_value(stream, "language"),
            "language_name": None,  # Could be enhanced with language mapping
            "size": get_value(stream, "filesize", convert_to=int),
            "youtube_format_id": int(format_id) if format_id.isdigit() else None,
        }

    @staticmethod
    def convert_subtitle_stream(subtitle: dict[str, Any], language_code: str) -> dict[str, Any]:
        """Convert raw subtitle stream to clean format."""
        return {
            "url": get_value(subtitle, "url", convert_to=[unquote, strip_whitespace]),
            "extension": get_value(subtitle, "ext", default_to="srt"),
            "language": language_code,
            "language_name": get_value(subtitle, "name"),
            "is_auto_generated": False,  # Would need detection logic
            "is_translatable": False,  # Would need detection logic
            "is_fragment_based": False,  # Would need detection logic
            "youtube_format_id": get_value(subtitle, "format_id"),
        }


class VideoInfoExtractor:
    """Extract and clean video information."""

    @staticmethod
    def extract_info(raw_data: dict[str, Any], source_url: str | None = None) -> dict[str, Any]:
        """Extract video information from raw data."""
        video_id = get_value(raw_data, "id")
        title = get_value(raw_data, "fulltitle", ["title"])
        description = get_value(raw_data, "description")
        channel_name = get_value(raw_data, "channel", ["uploader"])

        chapters = [
            {
                "title": get_value(chapter, "title"),
                "start_time": get_value(chapter, "start_time", convert_to=float),
                "end_time": get_value(chapter, "end_time", convert_to=float),
            }
            for chapter in get_value(raw_data, "chapters", convert_to=list, default_to=[])
        ]

        return {
            "source_url": source_url,
            "short_url": f"https://youtu.be/{video_id}" if video_id else None,
            "embed_url": f"https://www.youtube.com/embed/{video_id}" if video_id else None,
            "youtube_music_url": f"https://music.youtube.com/watch?v={video_id}" if video_id else None,
            "full_url": f"https://www.youtube.com/watch?v={video_id}" if video_id else None,
            "id": video_id,
            "title": title,
            "description": description,
            "channel_id": get_value(raw_data, "channel_id"),
            "channel_url": get_value(raw_data, "channel_url", ["uploader_url"]),
            "channel_name": channel_name,
            "is_verified_channel": get_value(raw_data, "channel_is_verified", default_to=False),
            "duration": get_value(raw_data, "duration"),
            "view_count": get_value(raw_data, "view_count"),
            "is_age_restricted": get_value(raw_data, "age_limit", convert_to=bool),
            "categories": get_value(raw_data, "categories", default_to=[]),
            "tags": get_value(raw_data, "tags", default_to=[]),
            "is_streaming": get_value(raw_data, "is_live"),
            "upload_timestamp": get_value(raw_data, "timestamp", ["release_timestamp"]),
            "availability": get_value(raw_data, "availability"),
            "chapters": chapters,
            "comment_count": get_value(raw_data, "comment_count", convert_to=int, default_to=0),
            "like_count": get_value(raw_data, "like_count", convert_to=int),
            "dislike_count": None,  # Will be set separately if requested
            "follow_count": get_value(raw_data, "channel_follower_count", convert_to=int),
            "language": get_value(raw_data, "language"),
            "thumbnails": [
                f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                f"https://img.youtube.com/vi/{video_id}/sddefault.jpg",
                f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
                f"https://img.youtube.com/vi/{video_id}/default.jpg",
            ]
            if video_id
            else [],
        }
