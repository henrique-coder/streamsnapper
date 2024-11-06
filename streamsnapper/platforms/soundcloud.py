# Built-in imports
from re import compile as re_compile
from datetime import datetime
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

    def __init__(self) -> None:
        """Initialize the SoundCloud class."""

        self._extractor: Type[SoundCloud.Extractor] = self.Extractor()
        self._soundcloud_api: SoundcloudAPI = SoundcloudAPI(client_id='gJUfQ83SeoGM0qvM3VetdqVTDyHmSusF')
        self._soundcloud_track: SoundcloudTrack = None

        self.general_info: Dict[str, Any] = {}
        self.best_audio_stream: Dict[str, Any] = {}
        self.best_audio_download_url: Optional[str] = None

    def run(self, url: str) -> None:
        """
        Run the process of extracting and formatting data from a SoundCloud track or playlist.

        :param url: The SoundCloud track or playlist URL to extract data from.
        :raises ScrapingError: If an error occurs while scraping the SoundCloud track.
        """

        try:
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
            'description': self._soundcloud_track.description,
            'genre': self._soundcloud_track.genre,
            'tags': self._soundcloud_track.tag_list,
            'license': self._soundcloud_track.license,
        }

    def generate_audio_stream(self) -> None:
        """Extract and format the best audio stream."""

        self.best_audio_download_url = self._soundcloud_track.get_stream_url()


    class Extractor:
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
