"""Subtitle-related data models."""

from typing import Any

from pydantic import BaseModel, Field


class SubtitleStream(BaseModel):
    """Individual subtitle stream with comprehensive metadata."""

    # Stream info
    url: str
    extension: str

    # Language info
    language: str | None = None
    language_name: str | None = None

    # Properties
    is_auto_generated: bool = False
    is_translatable: bool = False
    is_fragment_based: bool = False
    size: int | None = None
    youtube_format_id: str | None = None

    @property
    def is_manual(self) -> bool:
        """Check if subtitle is manually created (not auto-generated)."""
        return not self.is_auto_generated

    @property
    def quality_score(self) -> float:
        """Calculate quality score for ranking (higher is better)."""
        score = 0.0

        # Manual subtitles are much higher quality
        if not self.is_auto_generated:
            score += 100

        # Translatable subtitles are useful
        if self.is_translatable:
            score += 10

        # Fragment-based subtitles might have better timing
        if self.is_fragment_based:
            score += 5

        # Certain formats are preferred
        format_priority = {
            "vtt": 10,  # WebVTT - best for web
            "srt": 8,  # SubRip - widely supported
            "ass": 6,  # Advanced SubStation - rich formatting
            "ssa": 4,  # SubStation Alpha
            "ttml": 3,  # TTML
            "srv3": 2,  # YouTube's format
        }

        score += format_priority.get(self.extension.lower(), 0)

        return score

    @property
    def format_name(self) -> str:
        """Get human-readable format name."""
        format_names = {
            "vtt": "WebVTT",
            "srt": "SubRip",
            "ass": "Advanced SubStation Alpha",
            "ssa": "SubStation Alpha",
            "ttml": "Timed Text Markup Language",
            "srv3": "YouTube Format",
        }

        return format_names.get(self.extension.lower(), self.extension.upper())

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()


class SubtitleStreamCollection(BaseModel):
    """Collection of subtitle streams with advanced filtering and utilities."""

    streams: list[SubtitleStream] = Field(default_factory=list)

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
    def available_formats(self) -> list[str]:
        """Get list of available subtitle formats."""
        formats = {stream.extension for stream in self.streams if stream.extension}
        return sorted(formats)

    @property
    def manual_subtitles(self) -> list[SubtitleStream]:
        """Get only manually created subtitles, sorted by quality."""
        return sorted([s for s in self.streams if s.is_manual], key=lambda s: s.quality_score, reverse=True)

    @property
    def auto_generated_subtitles(self) -> list[SubtitleStream]:
        """Get only auto-generated subtitles, sorted by quality."""
        return sorted([s for s in self.streams if s.is_auto_generated], key=lambda s: s.quality_score, reverse=True)

    @property
    def translatable_subtitles(self) -> list[SubtitleStream]:
        """Get only translatable subtitles, sorted by quality."""
        return sorted([s for s in self.streams if s.is_translatable], key=lambda s: s.quality_score, reverse=True)

    @property
    def fragment_based_subtitles(self) -> list[SubtitleStream]:
        """Get only fragment-based subtitles."""
        return sorted([s for s in self.streams if s.is_fragment_based], key=lambda s: s.quality_score, reverse=True)

    def get_by_language(self, language: str, fallback: bool = True) -> list[SubtitleStream]:
        """Get subtitles by language with fuzzy matching and optional fallback."""
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

    def get_by_type(self, manual_only: bool = False, auto_only: bool = False) -> list[SubtitleStream]:
        """Get subtitles by type (manual/auto-generated)."""
        if manual_only:
            return self.manual_subtitles
        elif auto_only:
            return self.auto_generated_subtitles
        else:
            return sorted(self.streams, key=lambda s: s.quality_score, reverse=True)

    def get_by_extension(self, extension: str) -> list[SubtitleStream]:
        """Get subtitles by file extension."""
        return sorted(
            [s for s in self.streams if s.extension.lower() == extension.lower()],
            key=lambda s: s.quality_score,
            reverse=True,
        )

    def get_best_for_language(self, language: str, prefer_manual: bool = True) -> SubtitleStream | None:
        """Get best subtitle for specific language with preference control."""
        language_streams = self.get_by_language(language, fallback=False)
        if not language_streams:
            return None

        if prefer_manual:
            manual_streams = [s for s in language_streams if s.is_manual]
            if manual_streams:
                return manual_streams[0]  # Already sorted by quality

        return language_streams[0]  # Best by quality score

    def get_by_format_preference(self, preferred_formats: list[str]) -> list[SubtitleStream]:
        """Get subtitles ordered by format preference."""
        result = []

        # Add streams in order of format preference
        for fmt in preferred_formats:
            fmt_streams = self.get_by_extension(fmt)
            result.extend(fmt_streams)

        # Add remaining streams
        used_streams = set(result)
        remaining = [s for s in self.streams if s not in used_streams]
        result.extend(sorted(remaining, key=lambda s: s.quality_score, reverse=True))

        return result

    def filter_by_quality_score(self, min_score: float = 0.0) -> list[SubtitleStream]:
        """Get subtitles with quality score above threshold."""
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
