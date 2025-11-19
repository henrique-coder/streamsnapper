"""Extractor and extraction result data models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .audio import AudioStreamCollection
from .subtitle import SubtitleStreamCollection
from .video import VideoInformation, VideoStreamCollection


class ExtractionMetadata(BaseModel):
    """Metadata about the extraction process."""

    extraction_timestamp: datetime = Field(default_factory=datetime.now)
    extractor_name: str = "yt-dlp"
    extractor_version: str | None = None
    source_url: str
    extraction_duration: float | None = None
    network_requests: int | None = None

    user_agent: str | None = None
    cookies_used: bool = False
    proxy_used: bool = False

    def to_json(self) -> str:
        return self.model_dump_json()

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


class ExtractionResult(BaseModel):
    """Complete extraction result with all streams and metadata."""

    video_info: VideoInformation
    video_streams: VideoStreamCollection = Field(default_factory=VideoStreamCollection)
    audio_streams: AudioStreamCollection = Field(default_factory=AudioStreamCollection)
    subtitle_streams: SubtitleStreamCollection = Field(default_factory=SubtitleStreamCollection)

    metadata: ExtractionMetadata

    raw_data: dict[str, Any] = Field(default_factory=dict)

    @property
    def has_video(self) -> bool:
        """Check if video streams are available."""
        return len(self.video_streams) > 0

    @property
    def has_audio(self) -> bool:
        """Check if audio streams are available."""
        return len(self.audio_streams) > 0

    @property
    def has_subtitles(self) -> bool:
        """Check if subtitle streams are available."""
        return len(self.subtitle_streams) > 0

    @property
    def is_audio_only(self) -> bool:
        """Check if this is audio-only content."""
        return self.has_audio and not self.has_video

    @property
    def is_complete(self) -> bool:
        """Check if extraction found all expected content."""
        return self.has_video or self.has_audio

    @property
    def available_languages(self) -> list[str]:
        """Get all available languages across audio and subtitles."""
        languages = set()

        languages.update(self.audio_streams.available_languages)
        languages.update(self.subtitle_streams.available_languages)

        return sorted(languages)

    @property
    def summary(self) -> dict[str, Any]:
        """Get summary of available content."""
        return {
            "video_qualities": self.video_streams.available_qualities,
            "audio_languages": self.audio_streams.available_languages,
            "subtitle_languages": self.subtitle_streams.available_languages,
            "has_manual_subtitles": len(self.subtitle_streams.manual_subtitles) > 0,
            "total_streams": len(self.video_streams) + len(self.audio_streams) + len(self.subtitle_streams),
            "duration": self.video_info.duration,
            "title": self.video_info.title,
        }

    def get_best_video(self, resolution: str | None = None, codec: str | None = None) -> Any:
        """Get best video stream with optional filters."""
        streams = self.video_streams.streams

        if resolution:
            streams = self.video_streams.get_by_resolution(resolution, fallback=True)

        if codec and streams:
            codec_streams = [s for s in streams if s.codec and s.codec.lower() == codec.lower()]
            if codec_streams:
                streams = codec_streams

        if not streams:
            return None

        return max(streams, key=lambda s: (s.height or 0, s.bitrate or 0))

    def get_best_audio(self, language: str | None = None, codec: str | None = None) -> Any:
        """Get best audio stream with optional filters."""
        streams = self.audio_streams.streams

        if language:
            streams = self.audio_streams.get_by_language(language, fallback=True)

        if codec and streams:
            codec_streams = [s for s in streams if s.codec and s.codec.lower() == codec.lower()]
            if codec_streams:
                streams = codec_streams

        if not streams:
            return None

        return max(streams, key=lambda s: s.quality_score)

    def get_best_subtitle(self, language: str | None = None, manual_only: bool = True) -> Any:
        """Get best subtitle stream with optional filters."""
        if language:
            return self.subtitle_streams.get_best_for_language(language)

        streams = self.subtitle_streams.manual_subtitles if manual_only else self.subtitle_streams.streams

        if not streams:
            return None

        return max(streams, key=lambda s: s.quality_score)

    def to_json(self) -> str:
        return self.model_dump_json()

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


class StreamDownloadInfo(BaseModel):
    """Information for downloading a specific stream."""

    url: str
    filename: str
    extension: str

    stream_type: str
    codec: str | None = None
    quality: str | None = None
    language: str | None = None

    size: int | None = None
    estimated_duration: float | None = None

    headers: dict[str, str] = Field(default_factory=dict)
    requires_auth: bool = False

    def to_json(self) -> str:
        return self.model_dump_json()

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


class DownloadPlan(BaseModel):
    """Complete download plan with selected streams."""

    video_stream: StreamDownloadInfo | None = None
    audio_stream: StreamDownloadInfo | None = None
    subtitle_streams: list[StreamDownloadInfo] = Field(default_factory=list)

    output_directory: str
    output_filename: str
    merge_video_audio: bool = True

    max_concurrent_downloads: int = 3
    retry_attempts: int = 3

    @property
    def total_streams(self) -> int:
        """Get total number of streams to download."""
        count = 0
        if self.video_stream:
            count += 1
        if self.audio_stream:
            count += 1
        count += len(self.subtitle_streams)
        return count

    @property
    def estimated_size(self) -> int | None:
        """Get estimated total download size."""
        total_size = 0
        size_known = False

        if self.video_stream and self.video_stream.size:
            total_size += self.video_stream.size
            size_known = True

        if self.audio_stream and self.audio_stream.size:
            total_size += self.audio_stream.size
            size_known = True

        for subtitle in self.subtitle_streams:
            if subtitle.size:
                total_size += subtitle.size
                size_known = True

        return total_size if size_known else None

    def to_json(self) -> str:
        return self.model_dump_json()

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
