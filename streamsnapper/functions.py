# Built-in modules
from collections.abc import Callable
from re import sub as re_sub
from typing import Any
from unicodedata import normalize


def get_value(
    data: dict[Any, Any],
    key: Any,
    fallback_keys: list[Any] | None = None,
    convert_to: Callable | list[Callable] | None = None,
    default_to: Any | None = None,
) -> Any:
    """
    Get a value from a dictionary or a list of fallback keys.

    - If the provided key does not exist in the dictionary, the function will return the default value if provided, or None otherwise.
    - If a list of fallback keys is provided, the function will try to get the value from the dictionary with the fallback keys. If the value is not found in the dictionary with any of the fallback keys, the function will return the default value if provided, or None otherwise.
    - If the value is not None and a conversion function or list of conversion functions is provided, the function will try to convert the value using each conversion function in sequence until one succeeds. If all conversions fail with ValueError or TypeError, the function will return the default value if provided, or None otherwise.

    Args:
        data: The dictionary to get the value from.
        key: The key to get the value from.
        fallback_keys: A list of fallback keys to try if the key does not exist in the dictionary. Defaults to None.
        convert_to: A conversion function or list of conversion functions to convert the value. Defaults to None.
        default_to: A default value to return if the value is not found in the dictionary or if all conversions fail. Defaults to None.

    Returns:
        The value from the dictionary or the default value if the value is not found in the dictionary or if all conversions fail.
    """

    try:
        value = data[key]
    except KeyError:
        value = None

    if value is None and fallback_keys:
        for fallback_key in fallback_keys:
            if fallback_key is not None:
                try:
                    value = data[fallback_key]

                    if value is not None:
                        break
                except KeyError:
                    continue

    if value is None:
        return default_to

    if convert_to is not None:
        converters = [convert_to] if not isinstance(convert_to, list) else convert_to

        for converter in converters:
            try:
                value = converter(value)
                break
            except (ValueError, TypeError):
                if converter == converters[-1]:
                    return default_to

                continue

    return value


def format_string(query: str, max_length: int | None = None) -> str | None:
    """
    Sanitizes a given string by removing all non-ASCII characters and non-alphanumeric characters, and trims it to a given maximum length.

    Args:
        query: The string to sanitize.
        max_length: The maximum length to trim the sanitized string to. Defaults to None.

    Returns:
        The sanitized string, or None if the sanitized string is empty.
    """

    if not query:
        return None

    normalized_string = normalize("NFKD", query).encode("ASCII", "ignore").decode("utf-8")
    sanitized_string = re_sub(r"\s+", " ", re_sub(r"[^a-zA-Z0-9\-_()[\]{}!$#+;,. ]", "", normalized_string)).strip()

    if max_length is not None and len(sanitized_string) > max_length:
        cutoff = sanitized_string[:max_length].rfind(" ")
        sanitized_string = sanitized_string[:cutoff] if cutoff != -1 else sanitized_string[:max_length]

    return sanitized_string if sanitized_string else None


def strip(string: Any) -> str:
    """
    Strips leading and trailing whitespace from a given string.

    Args:
        string: The string to strip.

    Returns:
        The stripped string.
    """

    return str(string).strip()
