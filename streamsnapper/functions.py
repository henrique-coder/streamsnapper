# Built-in imports
from pathlib import Path
from os import PathLike
from re import sub as re_sub
from unicodedata import normalize
from typing import Any, Union, Dict, Optional, Callable


def get_value(data: Dict[Any, Any], key: Any, fallback_key: Any = None, convert_to: Callable = None, default_to: Optional[Any] = None) -> Any:
    """
    Get a value from a dictionary, with optional fallback key, conversion and default value.

    :param data: The dictionary to search for the key.
    :param key: The key to search for in the dictionary.
    :param fallback_key: The fallback key to search for in the dictionary if the main key is not found.
    :param convert_to: The type to convert the value to. If the conversion fails, return the default value. If None, return the value as is.
    :param default_to: The default value to return if the key is not found.
    :return: The value from the dictionary. If the key is not found, return the default value.
    """

    try:
        value = data[key]
    except KeyError:
        if fallback_key is not None:
            try:
                value = data[fallback_key]
            except KeyError:
                return default_to
        else:
            return default_to

    if convert_to is not None:
        try:
            value = convert_to(value)
        except (ValueError, TypeError):
            return default_to

    return value


def format_string(query: str, max_length: int = 128) -> Optional[str]:
    """
    Format a string to be used as a filename or directory name. Remove special characters, limit length and normalize the string.

    :param query: The string to be formatted.
    :param max_length: The maximum length of the formatted string. If the string is longer, it will be truncated.
    :return: The formatted string. If the input string is empty, return None.
    """

    if not query:
        return None

    normalized_string = normalize('NFKD', query).encode('ASCII', 'ignore').decode('utf-8')
    sanitized_string = re_sub(r'\s+', ' ', re_sub(r'[^a-zA-Z0-9\-_()[\]{}!$#+;,. ]', '', normalized_string)).strip()

    if len(sanitized_string) > max_length:
        cutoff = sanitized_string[:max_length].rfind(' ')
        sanitized_string = sanitized_string[:cutoff] if cutoff != -1 else sanitized_string[:max_length]

    return sanitized_string if sanitized_string else None


def convert_to_path(file_path: Union[str, PathLike], check_if_exists: bool = True, check_if_is_file: bool = False, check_if_is_dir: bool = False) -> Path:
    """
    Convert a file path to a Path object. If the file does not exis, raise a FileExistsError. If the file is not a file, raise a FileNotFoundError. If the file is not a directory, raise a FileNotFoundError.

    :param file_path: The file path to convert.
    :param check_if_exists: If True, raise a FileExistsError if the file does not exist.
    :param check_if_is_file: If True, raise a FileNotFoundError if the file is not a file.
    :param check_if_is_dir: If True, raise a FileNotFoundError if the file is not a directory.
    :raises FileExistsError: If the file does not exist and check_if_exists is True.
    :raises FileNotFoundError: If the file is not a file and check_if_is_file is True or the file is not a directory and check_if_is_dir is True.
    :return: The Path object.
    """

    file_path = Path(file_path)

    if check_if_exists and not file_path.exists():
        raise FileExistsError(f'The path "{file_path}" does not exist.')

    if check_if_is_file and not file_path.is_file():
        raise FileNotFoundError(f'The path "{file_path}" is not a file.')

    if check_if_is_dir and not file_path.is_dir():
        raise FileNotFoundError(f'The path "{file_path}" is not a directory.')

    return file_path
