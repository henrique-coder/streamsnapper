# Standard modules
from locale import getlocale, setlocale, LC_ALL
from re import sub
from collections.abc import Callable
from typing import Any
from unicodedata import normalize
from json import JSONDecodeError
from contextlib import suppress
from enum import Enum
from pathlib import Path
from os import PathLike

# Third-party modules
from httpx import get, head

# Local modules
from .logger import logger


class SupportedCookieBrowser(str, Enum):
    """Supported browsers for extracting cookies."""

    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"
    OPERA = "opera"
    BRAVE = "brave"
    CHROMIUM = "chromium"


class CookieFile:
    """Represents a cookie file."""

    def __init__(self, file_path: str | PathLike) -> None:
        """
        Initialize cookie file.

        Args:
            file_path: Path to cookie file (Netscape format)
        """

        self.path = Path(file_path)

        if not self.path.exists():
            logger.warning(f"Cookie file does not exist: {self.path}")
        elif not self.path.is_file():
            raise ValueError(f"Cookie path is not a file: {self.path}")
        else:
            logger.debug(f"Cookie file initialized: {self.path}")

    def __str__(self) -> str:
        """Return file path as string."""

        return self.path.as_posix()

    def __repr__(self) -> str:
        """Return representation of cookie file."""

        return f"CookieFile('{self.path}')"


def get_value(
    data: dict[Any, Any],
    key: Any,
    fallback_keys: list[Any] | None = None,
    convert_to: Callable | list[Callable] | None = None,
    default_to: Any = None,
) -> Any:
    """
    Extract value from dictionary with fallback keys and type conversion.

    Args:
        data: The dictionary to extract value from
        key: Primary key to look for
        fallback_keys: Alternative keys if primary key fails
        convert_to: Function(s) to convert the value
        default_to: Default value if extraction/conversion fails

    Returns:
        Extracted and converted value or default
    """

    logger.trace(f"Extracting value for key: {key}")

    # Try primary key
    value = data.get(key)

    # Try fallback keys if primary key failed
    if value is None and fallback_keys:
        for fallback_key in fallback_keys:
            if fallback_key is not None:
                value = data.get(fallback_key)

                if value is not None:
                    logger.trace(f"Found value using fallback key: {fallback_key}")
                    break

    if value is None:
        logger.trace(f"No value found for key {key}, returning default: {default_to}")

        return default_to

    # Apply conversions if specified
    if convert_to is not None:
        converters = [convert_to] if not isinstance(convert_to, list) else convert_to

        for converter in converters:
            try:
                converted_value = converter(value)
                logger.trace(f"Successfully converted value using {converter.__name__}")

                return converted_value
            except (ValueError, TypeError) as e:
                logger.trace(f"Conversion failed with {converter.__name__}: {repr(e)}")

                if converter == converters[-1]:
                    logger.warning(f"All conversions failed for key {key}, returning default")

                    return default_to

                continue

    return value


def sanitize_filename(text: str, max_length: int | None = 255, replacement_char: str = "_") -> str | None:
    """
    Sanitize text for use as filename.

    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        replacement_char: Character to replace invalid chars with

    Returns:
        Sanitized filename or None if empty after sanitization
    """

    if not text:
        logger.warning("Empty text provided for filename sanitization")

        return None

    logger.trace(f"Sanitizing filename: {text[:100]}...")

    # Normalize unicode characters
    normalized = normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")

    # Remove invalid filename characters
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = sub(invalid_chars, replacement_char, normalized)

    # Clean up multiple spaces/underscores
    sanitized = sub(r"[\s_]+", replacement_char, sanitized).strip("_. ")

    # Truncate if necessary
    if max_length and len(sanitized) > max_length:
        # Try to cut at word boundary
        cutoff = sanitized[:max_length].rfind(" ")
        sanitized = sanitized[:cutoff] if cutoff != -1 else sanitized[:max_length]

    result = sanitized if sanitized else None
    logger.trace(f"Sanitized filename result: {result}")

    return result


def format_duration(seconds: int | None) -> str:
    """
    Format duration in seconds to human readable format (HH:MM:SS).

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string (HH:MM:SS) or "Unknown" if None
    """

    if seconds is None:
        return "Unknown"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def strip_whitespace(value: Any) -> str:
    """
    Strip whitespace from any value converted to string.

    Args:
        value: Value to strip

    Returns:
        Stripped string
    """

    return str(value).strip()


def detect_system_language(fallback: str = "en-US") -> str:
    """
    Detect system language using the most reliable method.

    Args:
        fallback: Fallback language code if detection fails

    Returns:
        Language code in format "en-US" (fallback: "en-US")
    """

    try:
        # Set locale to system default and get it
        setlocale(LC_ALL, "")
        system_locale = getlocale()[0]

        if system_locale and "_" in system_locale:
            # Convert from "en_US" to "en-US" format
            language_code = system_locale.split(".")[0].replace("_", "-")
            logger.debug(f"Detected system language: {language_code}")

            return language_code
    except Exception as e:
        logger.warning(f"Language detection failed: {repr(e)}")

    # Fallback
    logger.info(f"Using fallback language: {fallback}")

    return fallback


def filter_valid_youtube_thumbnails(thumbnails: list[str]) -> list[str]:
    """
    Filter YouTube thumbnail URLs, returning list starting from first valid thumbnail.
    Stops at first valid thumbnail found.

    Args:
        thumbnails: List of YouTube thumbnail URLs to validate

    Returns:
        List starting from first valid thumbnail, or empty list if none valid
    """

    if not thumbnails:
        return []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    }

    for index, url in enumerate(thumbnails):
        try:
            response = head(url, headers=headers, follow_redirects=False, timeout=5)

            if response.is_success:
                logger.trace(f"First valid YouTube thumbnail found: {url}")

                return thumbnails[index:]
            else:
                logger.trace(f"Invalid YouTube thumbnail (non-success response): {url}")
        except Exception as e:
            logger.trace(f"Invalid YouTube thumbnail (request exception): {url} - {repr(e)}")

    logger.debug("No valid YouTube thumbnails found")

    return []


def get_youtube_dislike_count(video_id: str) -> int | None:
    """
    Retrieve dislike count for YouTube video from external API.

    Args:
        video_id: YouTube video ID

    Returns:
        Dislike count as integer or None if unavailable/failed
    """

    try:
        response = get(
            "https://returnyoutubedislikeapi.com/votes",
            params={"videoId": video_id},
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
            },
        )

        if response.is_success:
            with suppress(JSONDecodeError):
                dislike_count = get_value(response.json(), "dislikes", convert_to=int)

                if dislike_count is not None:
                    logger.trace(f"Retrieved dislike count for {video_id}: {dislike_count}")

                    return dislike_count
                else:
                    logger.trace(f"No dislike data available for video: {video_id}")
        else:
            logger.trace(f"Failed to fetch dislike count (non-success response): {video_id}")
    except Exception as e:
        logger.trace(f"Failed to fetch dislike count (request exception): {video_id} - {repr(e)}")

    return None
