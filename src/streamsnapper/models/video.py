"""Video-related data models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class VideoInformation(BaseModel):
    """Complete video information with comprehensive metadata."""

    # URLs
    source_url: str | None = None
    short_url: str | None = None
    embed_url: str | None = None
    youtube_music_url: str | None = None
    full_url: str | None = None

    # Basic video info
    id: str | None = None
    title: str | None = None
    clean_title: str | None = None
    description: str | None = None

    # Channel info
    channel_id: str | None = None
    channel_url: str | None = None
    channel_name: str | None = None
    clean_channel_name: str | None = None
    is_verified_channel: bool = False

    # Metrics
    duration: int | None = None
    view_count: int | None = None
    like_count: int | None = None
    dislike_count: int | None = None
    comment_count: int | None = None
    follow_count: int | None = None

    # Properties
    is_age_restricted: bool = False
    categories: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    chapters: list[dict[str, Any]] = Field(default_factory=list)
    is_streaming: bool = False
    upload_timestamp: int | None = None
    availability: str | None = None
    language: str | None = None

    # Media
    thumbnails: list[str] = Field(default_factory=list)

    @property
    def upload_date(self) -> datetime | None:
        """Get upload date as datetime object."""
        if self.upload_timestamp:
            return datetime.fromtimestamp(self.upload_timestamp)
        return None

    @property
    def duration_formatted(self) -> str:
        """Get formatted duration (HH:MM:SS)."""
        if not self.duration:
            return "Unknown"

        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60

        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()


class VideoStream(BaseModel):
    """Individual video stream with comprehensive metadata."""

    # Stream info
    url: str
    codec: str | None = None
    codec_variant: str | None = None
    raw_codec: str | None = None
    extension: str

    # Video properties
    width: int | None = None
    height: int | None = None
    quality: int | None = None
    framerate: float | None = None
    bitrate: float | None = None

    # Additional metadata
    quality_note: str | None = None
    is_hdr: bool = False
    size: int | None = None
    language: str | None = None
    youtube_format_id: int | None = None

    @property
    def resolution(self) -> str | None:
        """Get resolution string like '1080p'."""
        if self.height:
            return f"{self.height}p"
        return None

    @property
    def aspect_ratio(self) -> float | None:
        """Get aspect ratio (width/height)."""
        if self.width and self.height:
            return round(self.width / self.height, 2)
        return None

    @property
    def quality_score(self) -> float:
        """Calculate quality score for ranking."""
        score = 0.0

        if self.width and self.height:
            score += (self.width * self.height) / 1000000  # Megapixels

        if self.framerate:
            score += self.framerate / 10

        if self.bitrate:
            score += self.bitrate / 100

        if self.is_hdr:
            score += 10

        return round(score, 2)

    @property
    def is_hd(self) -> bool:
        """Check if stream is HD (>=720p)."""
        return (self.height or 0) >= 720

    @property
    def is_4k(self) -> bool:
        """Check if stream is 4K (>=2160p)."""
        return (self.height or 0) >= 2160

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()


class VideoStreamCollection(BaseModel):
    """Collection of video streams with advanced filtering and utilities."""

    streams: list[VideoStream] = Field(default_factory=list)

    @property
    def has_streams(self) -> bool:
        """Check if collection has any streams."""
        return len(self.streams) > 0

    @property
    def available_qualities(self) -> list[str]:
        """Get list of available qualities sorted by resolution."""
        qualities = {stream.resolution for stream in self.streams if stream.resolution}
        return sorted(qualities, key=lambda x: int(x.replace("p", "")), reverse=True)

    @property
    def available_codecs(self) -> list[str]:
        """Get list of available codecs."""
        codecs = {stream.codec for stream in self.streams if stream.codec}
        return sorted(codecs)

    @property
    def best_stream(self) -> VideoStream | None:
        """Get highest quality stream based on quality score."""
        if not self.streams:
            return None
        return max(self.streams, key=lambda s: s.quality_score)

    @property
    def worst_stream(self) -> VideoStream | None:
        """Get lowest quality stream based on quality score."""
        if not self.streams:
            return None
        return min(self.streams, key=lambda s: s.quality_score)

    @property
    def hd_streams(self) -> list[VideoStream]:
        """Get only HD streams (>=720p)."""
        return [s for s in self.streams if s.is_hd]

    @property
    def uhd_streams(self) -> list[VideoStream]:
        """Get only UHD/4K streams (>=2160p)."""
        return [s for s in self.streams if s.is_4k]

    @property
    def hdr_streams(self) -> list[VideoStream]:
        """Get only HDR streams."""
        return [s for s in self.streams if s.is_hdr]

    def get_by_resolution(self, resolution: str, fallback: bool = True) -> list[VideoStream]:
        """Get streams by resolution with optional fallback to lower quality."""
        target_height = int(resolution.replace("p", ""))

        exact_matches = [s for s in self.streams if s.height == target_height]
        if exact_matches:
            return sorted(exact_matches, key=lambda s: s.quality_score, reverse=True)

        if fallback:
            fallback_streams = [s for s in self.streams if s.height and s.height <= target_height]
            if fallback_streams:
                best_fallback_height = max(s.height for s in fallback_streams)
                return sorted(
                    [s for s in fallback_streams if s.height == best_fallback_height], key=lambda s: s.quality_score, reverse=True
                )

        return []

    def get_by_codec(self, codec: str) -> list[VideoStream]:
        """Get streams by codec type."""
        return [s for s in self.streams if s.codec and s.codec.lower() == codec.lower()]

    def get_by_framerate_range(self, min_fps: float | None = None, max_fps: float | None = None) -> list[VideoStream]:
        """Get streams within framerate range."""
        filtered = self.streams

        if min_fps is not None:
            filtered = [s for s in filtered if s.framerate and s.framerate >= min_fps]

        if max_fps is not None:
            filtered = [s for s in filtered if s.framerate and s.framerate <= max_fps]

        return sorted(filtered, key=lambda s: s.quality_score, reverse=True)

    def get_by_bitrate_range(self, min_bitrate: float | None = None, max_bitrate: float | None = None) -> list[VideoStream]:
        """Get streams within bitrate range."""
        filtered = self.streams

        if min_bitrate is not None:
            filtered = [s for s in filtered if s.bitrate and s.bitrate >= min_bitrate]

        if max_bitrate is not None:
            filtered = [s for s in filtered if s.bitrate and s.bitrate <= max_bitrate]

        return sorted(filtered, key=lambda s: s.quality_score, reverse=True)

    def filter_by_quality_score(self, min_score: float = 0.0) -> list[VideoStream]:
        """Get streams with quality score above threshold."""
        return [s for s in self.streams if s.quality_score >= min_score]

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()

    def __len__(self) -> int:
        return len(self.streams)

    def __iter__(self):
        return iter(self.streams)

    def __getitem__(self, index):
        return self.streams[index]
