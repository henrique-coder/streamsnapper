"""Audio-related data models."""

from typing import Any

from pydantic import BaseModel, Field


class AudioStream(BaseModel):
    """Individual audio stream with comprehensive metadata."""

    # Stream info
    url: str
    codec: str | None = None
    codec_variant: str | None = None
    raw_codec: str | None = None
    extension: str

    # Audio properties
    bitrate: float | None = None
    sample_rate: int | None = None
    channels: int | None = None

    # Language and metadata
    language: str | None = None
    language_name: str | None = None
    size: int | None = None
    youtube_format_id: int | None = None

    @property
    def quality_score(self) -> float:
        """Calculate quality score for ranking."""
        score = 0.0

        if self.bitrate:
            score += self.bitrate * 10

        if self.sample_rate:
            score += self.sample_rate / 1000

        if self.channels:
            score += self.channels * 5

        return round(score, 2)

    @property
    def is_stereo(self) -> bool:
        """Check if audio is stereo (2 channels)."""

        return self.channels == 2 if self.channels else False

    @property
    def is_mono(self) -> bool:
        """Check if audio is mono (1 channel)."""

        return self.channels == 1 if self.channels else False

    @property
    def is_surround(self) -> bool:
        """Check if audio is surround sound (>2 channels)."""

        return (self.channels or 0) > 2

    @property
    def is_high_quality(self) -> bool:
        """Check if audio meets high quality standards (>=128kbps, >=44.1kHz)."""

        return (self.bitrate or 0) >= 128 and (self.sample_rate or 0) >= 44100

    @property
    def is_lossless_quality(self) -> bool:
        """Check if audio might be lossless quality (>=320kbps, >=48kHz)."""

        return (self.bitrate or 0) >= 320 and (self.sample_rate or 0) >= 48000

    @property
    def channel_description(self) -> str:
        """Get human-readable channel description."""

        if not self.channels:
            return "Unknown"

        channel_map = {1: "Mono", 2: "Stereo", 4: "Quadraphonic", 6: "5.1 Surround", 8: "7.1 Surround"}

        return channel_map.get(self.channels, f"{self.channels} channels")

    def to_json(self) -> str:
        """Convert to JSON string."""

        return self.model_dump_json()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""

        return self.model_dump()


class AudioStreamCollection(BaseModel):
    """Collection of audio streams with advanced filtering and utilities."""

    streams: list[AudioStream] = Field(default_factory=list)

    @property
    def has_streams(self) -> bool:
        """Check if collection has any streams."""

        return len(self.streams) > 0

    @property
    def available_languages(self) -> list[str]:
        """Get list of available language codes."""

        languages = {stream.language for stream in self.streams if stream.language}

        return sorted(languages)

    @property
    def available_language_names(self) -> list[str]:
        """Get list of available language names."""

        names = {stream.language_name for stream in self.streams if stream.language_name}

        return sorted(names)

    @property
    def available_codecs(self) -> list[str]:
        """Get list of available audio codecs."""

        codecs = {stream.codec for stream in self.streams if stream.codec}

        return sorted(codecs)

    @property
    def best_stream(self) -> AudioStream | None:
        """Get highest quality stream based on quality score."""

        if not self.streams:
            return None

        return max(self.streams, key=lambda s: s.quality_score)

    @property
    def worst_stream(self) -> AudioStream | None:
        """Get lowest quality stream based on quality score."""

        if not self.streams:
            return None

        return min(self.streams, key=lambda s: s.quality_score)

    @property
    def high_quality_streams(self) -> list[AudioStream]:
        """Get only high quality streams (>=128kbps, >=44.1kHz)."""

        return [s for s in self.streams if s.is_high_quality]

    @property
    def lossless_quality_streams(self) -> list[AudioStream]:
        """Get only lossless quality streams (>=320kbps, >=48kHz)."""

        return [s for s in self.streams if s.is_lossless_quality]

    @property
    def stereo_streams(self) -> list[AudioStream]:
        """Get only stereo streams."""

        return [s for s in self.streams if s.is_stereo]

    @property
    def surround_streams(self) -> list[AudioStream]:
        """Get only surround sound streams."""

        return [s for s in self.streams if s.is_surround]

    def get_by_language(self, language: str, fallback: bool = True) -> list[AudioStream]:
        """Get streams by language with fuzzy matching and optional fallback."""

        language_lower = language.lower()

        # Exact language code match
        exact_matches = [s for s in self.streams if s.language and s.language.lower() == language_lower]

        if exact_matches:
            return sorted(exact_matches, key=lambda s: s.quality_score, reverse=True)

        # Exact language name match
        name_matches = [s for s in self.streams if s.language_name and s.language_name.lower() == language_lower]

        if name_matches:
            return sorted(name_matches, key=lambda s: s.quality_score, reverse=True)

        # Partial matches (prefix matching for language variants)
        partial_matches = [
            s
            for s in self.streams
            if (
                s.language
                and (language_lower in s.language.lower() or s.language.lower().startswith(language_lower[:2]))
            )
            or (s.language_name and language_lower in s.language_name.lower())
        ]

        if partial_matches:
            return sorted(partial_matches, key=lambda s: s.quality_score, reverse=True)

        if fallback:
            return sorted(self.streams, key=lambda s: s.quality_score, reverse=True)

        return []

    def get_by_codec(self, codec: str) -> list[AudioStream]:
        """Get streams by codec type."""

        return sorted(
            [s for s in self.streams if s.codec and s.codec.lower() == codec.lower()],
            key=lambda s: s.quality_score,
            reverse=True,
        )

    def get_high_quality(self) -> list[AudioStream]:
        """Get only high quality streams sorted by quality score."""

        return sorted([s for s in self.streams if s.is_high_quality], key=lambda s: s.quality_score, reverse=True)

    def get_by_bitrate_range(
        self, min_bitrate: float | None = None, max_bitrate: float | None = None
    ) -> list[AudioStream]:
        """Get streams within bitrate range."""

        filtered = self.streams

        if min_bitrate is not None:
            filtered = [s for s in filtered if s.bitrate and s.bitrate >= min_bitrate]

        if max_bitrate is not None:
            filtered = [s for s in filtered if s.bitrate and s.bitrate <= max_bitrate]

        return sorted(filtered, key=lambda s: s.quality_score, reverse=True)

    def get_by_sample_rate_range(self, min_rate: int | None = None, max_rate: int | None = None) -> list[AudioStream]:
        """Get streams within sample rate range."""

        filtered = self.streams

        if min_rate is not None:
            filtered = [s for s in filtered if s.sample_rate and s.sample_rate >= min_rate]

        if max_rate is not None:
            filtered = [s for s in filtered if s.sample_rate and s.sample_rate <= max_rate]

        return sorted(filtered, key=lambda s: s.quality_score, reverse=True)

    def get_by_channel_count(self, channels: int) -> list[AudioStream]:
        """Get streams with specific channel count."""

        return sorted([s for s in self.streams if s.channels == channels], key=lambda s: s.quality_score, reverse=True)

    def filter_by_quality_score(self, min_score: float = 0.0) -> list[AudioStream]:
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

    def __iter__(self) -> Any:
        return iter(self.streams)

    def __getitem__(self, index) -> Any:
        return self.streams[index]
