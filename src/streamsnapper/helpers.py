"""General utility functions for StreamSnapper."""

from collections.abc import Callable
import re
from typing import Any
from urllib.parse import unquote


def clean_url(url: str) -> str:
    """Clean and decode URL."""
    return unquote(url).strip()


def extract_codec_parts(codec: str | None) -> tuple[str | None, str | None]:
    """Extract main codec and variant from codec string."""
    if not codec:
        return None, None

    parts = codec.split(".", 1)
    return parts[0], parts[1] if len(parts) > 1 else None


def calculate_aspect_ratio(width: int | None, height: int | None) -> float | None:
    """Calculate aspect ratio from width and height."""
    if width and height:
        return width / height
    return None


def format_resolution(height: int | None) -> str | None:
    """Format height as resolution string (e.g., '1080p')."""
    if height:
        return f"{height}p"
    return None


def parse_format_id(format_id: str | int) -> int | None:
    """Parse format ID to integer, handling various input types."""
    if isinstance(format_id, int):
        return format_id

    if isinstance(format_id, str):
        # Handle format IDs like "251-en" by taking the first part
        base_id = format_id.split("-")[0]
        if base_id.isdigit():
            return int(base_id)

    return None


def is_hdr_content(quality_note: str | None) -> bool:
    """Check if content is HDR based on quality note."""
    if not quality_note:
        return False
    return "hdr" in quality_note.lower()


def safe_apply(func: Callable, value: Any, default: Any = None) -> Any:
    """Safely apply function to value, returning default on error."""
    try:
        return func(value) if value is not None else default
    except (ValueError, TypeError, AttributeError):
        return default


def normalize_language_code(language: str | None) -> str | None:
    """Normalize language code to lowercase."""
    return language.lower() if language else None


def extract_quality_from_note(quality_note: str | None) -> int | None:
    """Extract numeric quality from quality note string."""
    if not quality_note:
        return None

    # Look for patterns like "1080p", "720p60", etc.
    match = re.search(r"(\d+)p", quality_note.lower())
    if match:
        return int(match.group(1))

    return None


def is_high_quality_audio(bitrate: float | None, sample_rate: int | None) -> bool:
    """Check if audio stream meets high quality thresholds."""
    return (bitrate or 0) >= 128 and (sample_rate or 0) >= 44100


def is_stereo_audio(channels: int | None) -> bool:
    """Check if audio is stereo (2 channels)."""
    return channels == 2 if channels else False


def sort_by_quality(streams: list[Any], key_func: Callable[[Any], float], reverse: bool = True) -> list[Any]:
    """Sort streams by quality using provided key function."""
    return sorted(streams, key=key_func, reverse=reverse)


def filter_by_attribute(streams: list[Any], attribute: str, value: Any, case_sensitive: bool = False) -> list[Any]:
    """Filter streams by attribute value."""
    filtered = []

    for stream in streams:
        stream_value = getattr(stream, attribute, None)

        if stream_value is None:
            continue

        if isinstance(stream_value, str) and isinstance(value, str) and not case_sensitive:
            if stream_value.lower() == value.lower():
                filtered.append(stream)
        elif stream_value == value:
            filtered.append(stream)

    return filtered


def find_best_match(streams: list[Any], target_value: Any, key_func: Callable[[Any], Any]) -> Any | None:
    """Find stream with best matching value."""
    if not streams:
        return None

    # Try exact match first
    for stream in streams:
        if key_func(stream) == target_value:
            return stream

    return None


def calculate_file_size_mb(size_bytes: int | None) -> float | None:
    """Convert file size from bytes to megabytes."""
    if size_bytes is None:
        return None
    return size_bytes / (1024 * 1024)


def format_duration(seconds: int | None) -> str | None:
    """Format duration in seconds to human readable format."""
    if seconds is None:
        return None

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def validate_url(url: str | None) -> bool:
    """Basic URL validation."""
    if not url:
        return False

    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    return bool(url_pattern.match(url))


def truncate_string(text: str | None, max_length: int = 100) -> str | None:
    """Truncate string to maximum length with ellipsis."""
    if not text:
        return text

    if len(text) <= max_length:
        return text

    return text[: max_length - 3] + "..."
