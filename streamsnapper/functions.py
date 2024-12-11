# Built-in imports
from re import sub as re_sub
from typing import Any, Callable, Dict, List, Optional
from unicodedata import normalize


def get_value(
    data: Dict[Any, Any],
    key: Any,
    fallback_keys: Optional[List[Any]] = None,
    convert_to: Optional[Callable] = None,
    default_to: Optional[Any] = None,
) -> Any:
    """
    Get a value from a dictionary or a list of fallback keys.

    If the provided key does not exist in the dictionary, the function will return the default value if provided, or None otherwise.

    If a list of fallback keys is provided, the function will try to get the value from the dictionary with the fallback keys. If the value is not found in the dictionary with any of the fallback keys, the function will return the default value if provided, or None otherwise.

    If the value is not None and a conversion function is provided, the function will try to convert the value using the provided conversion function. If the conversion fails with a ValueError or TypeError, the function will return the default value if provided, or None otherwise.

    Args:
        data: The dictionary to get the value from. (required)
        key: The key to get the value from. (required)
        fallback_keys: A list of fallback keys to try if the key does not exist in the dictionary. (default: None)
        convert_to: A conversion function to convert the value. (default: None)
        default_to: A default value to return if the value is not found in the dictionary or if the conversion fails. (default: None)

    Returns:
        The value from the dictionary or the default value if the value is not found in the dictionary or if the conversion fails.
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
        try:
            value = convert_to(value)
        except (ValueError, TypeError):
            return default_to

    return value


def format_string(query: str, max_length: Optional[int] = None) -> Optional[str]:
    """
    Sanitizes a given string by removing all non-ASCII characters and non-alphanumeric characters, and trims it to a given maximum length.

    Args:
        query: The string to sanitize. (required)
        max_length: The maximum length to trim the sanitized string to. (default: None)

    Returns:
        The sanitized string, or None if the sanitized string is empty.
    """

    if not query:
        return None

    normalized_string = normalize('NFKD', query).encode('ASCII', 'ignore').decode('utf-8')
    sanitized_string = re_sub(r'\s+', ' ', re_sub(r'[^a-zA-Z0-9\-_()[\]{}!$#+;,. ]', '', normalized_string)).strip()

    if max_length is not None and len(sanitized_string) > max_length:
        cutoff = sanitized_string[:max_length].rfind(' ')
        sanitized_string = sanitized_string[:cutoff] if cutoff != -1 else sanitized_string[:max_length]

    return sanitized_string if sanitized_string else None
