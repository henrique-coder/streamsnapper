# Built-in imports
from pathlib import Path
from re import compile as re_compile
from datetime import datetime
from tempfile import gettempdir
from io import StringIO
from contextlib import redirect_stderr
from typing import Any, Dict, Optional, Type

# Third-party imports
try:
    from sclib import SoundcloudAPI, Track as SoundcloudTrack
except (ImportError, ModuleNotFoundError):
    pass

# Local imports
from ..exceptions import ScrapingError


class SoundCloud:
    """A class for extracting and formatting data from SoundCloud tracks and playlists, facilitating access to general track information and audio streams."""

    def _get_client_id(self) -> Optional[str]:
        if self._temporary_file_path.exists():
            found_text = self._temporary_file_path.read_text().strip()

            return found_text if found_text else None

    def _set_client_id(self, client_id: str) -> str:
        self._temporary_file_path.write_text(client_id)

    def __init__(self, enable_token_cache: bool = True) -> None:
        """
        Initialize the SoundCloud class.

        :param enable_token_cache: Enable or disable token caching for the SoundcloudAPI to improve performance and reduce rate limits.
        """

        self._temporary_file_path = Path(gettempdir(), '.tmp-soundcloud-scraped-client-id.txt').resolve()
        _client_id = self._get_client_id()

        if enable_token_cache and _client_id:
            self._soundcloud_api: SoundcloudAPI = SoundcloudAPI(client_id=_client_id)
        else:
            self._soundcloud_api: SoundcloudAPI = SoundcloudAPI()
            self._soundcloud_api.get_credentials()
            self._set_client_id(self._soundcloud_api.client_id)

        self._extractor: Type[SoundCloudExtractor] = SoundCloudExtractor()
        self._soundcloud_track: SoundcloudTrack = None

        self.general_info: Dict[str, Any] = {}
        self.best_audio_stream: Dict[str, Any] = {}
        self.best_audio_download_url: Optional[str] = None

    def extract(self, url: str) -> None:
        """
        Extract general track and audio stream information from a SoundCloud track or playlist.

        :param url: The SoundCloud track or playlist URL to extract data from.
        :raises ScrapingError: If an error occurs while scraping the SoundCloud track.
        """

        silent_buffer = StringIO()

        try:
            with redirect_stderr(silent_buffer):
                self._soundcloud_track = self._soundcloud_api.resolve(url)
        except TypeError as e:
            self._soundcloud_api.client_id = None
            self._soundcloud_api.get_credentials()
            self._set_client_id(self._soundcloud_api.client_id)
            self._soundcloud_track = self._soundcloud_api.resolve(url)
        except Exception as e:
            raise ScrapingError(f'Error occurred while scraping SoundCloud track: "{url}"') from e

    def analyze_info(self) -> None:
        """Extract and format relevant information."""

        self.general_info = {
            'id': self._soundcloud_track.id,
            'userId': self._soundcloud_track.user_id,
            'username': self._soundcloud_track.user['username'],
            'userAvatar': self._soundcloud_track.user['avatar_url'].replace('-large', '-original'),
            'title': self._soundcloud_track.title,
            'artist': self._soundcloud_track.artist,
            'duration': self._soundcloud_track.duration,
            'fullUrl': self._soundcloud_track.permalink_url,
            'thumbnail': self._soundcloud_track.artwork_url.replace('-large', '-original'),
            'commentCount': self._soundcloud_track.comment_count,
            'likeCount': self._soundcloud_track.likes_count,
            'downloadCount': self._soundcloud_track.download_count,
            'playbackCount': self._soundcloud_track.playback_count,
            'repostCount': self._soundcloud_track.reposts_count,
            'uploadTimestamp': int(datetime.fromisoformat(self._soundcloud_track.created_at.replace('Z', '+00:00')).timestamp()),
            'lastModifiedTimestamp': int(datetime.fromisoformat(self._soundcloud_track.last_modified.replace('Z', '+00:00')).timestamp()),
            'isCommentable': self._soundcloud_track.commentable,
            'description': self._soundcloud_track.description if self._soundcloud_track.description else None,
            'genre': self._soundcloud_track.genre,
            'license': self._soundcloud_track.license,
        }

    def generate_audio_stream(self) -> None:
        """Extract and format the best audio stream."""

        self.best_audio_download_url = self._soundcloud_track.get_stream_url()


class SoundCloudExtractor:
    """A class for extracting data from SoundCloud URLs and searching for SoundCloud tracks."""

    def __init__(self) -> None:
        """Initialize the Extractor class with some regular expressions for analyzing SoundCloud URLs."""

        self._track_id_regex = re_compile(r'(?:soundcloud\.com/|snd\.sc/)([^/]+)/(?!sets)([^/]+)')
        self._playlist_id_regex = re_compile(r'(?:soundcloud\.com/|snd\.sc/)([^/]+)/sets/([^/]+)')

    def extract_track_slug(self, url: str) -> Optional[str]:
        """
        Extract the SoundCloud track slug from a URL.

        :param url: The URL to extract the track slug from.
        :return: The extracted track slug. If no track slug is found, return None.
        """

        found_match = self._track_id_regex.search(url)
        return f'{found_match.group(1)}/{found_match.group(2)}' if found_match else None

    def extract_playlist_slug(self, url: str) -> Optional[str]:
        """
        Extract the SoundCloud playlist slug from a URL.

        :param url: The URL to extract the playlist slug from.
        :return: The extracted playlist slug. If no playlist slug is found, return None.
        """

        found_match = self._playlist_id_regex.search(url)
        return f'{found_match.group(1)}/sets/{found_match.group(2)}' if found_match else None
