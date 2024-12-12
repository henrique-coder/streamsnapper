## StreamSnapper

StreamSnapper is an intuitive library designed to simplify, enhance, and organize media downloads from a variety of audiovisual platforms. It offers efficient, high-speed media extraction with optional tools for extracting data from these platforms.

![PyPI - Version](https://img.shields.io/pypi/v/streamsnapper?style=flat&logo=pypi&logoColor=blue&color=blue&link=https://pypi.org/project/streamsnapper)
![PyPI - Downloads](https://img.shields.io/pypi/dm/streamsnapper?style=flat&logo=pypi&logoColor=blue&color=blue&link=https://pypi.org/project/streamsnapper)
![PyPI - Code Style](https://img.shields.io/badge/code%20style-ruff-blue?style=flat&logo=ruff&logoColor=blue&color=blue&link=https://github.com/astral-sh/ruff)
![PyPI - Format](https://img.shields.io/pypi/format/streamsnapper?style=flat&logo=pypi&logoColor=blue&color=blue&link=https://pypi.org/project/streamsnapper)
![PyPI - License](https://img.shields.io/pypi/l/streamsnapper?style=flat&logo=github&logoColor=blue&color=blue&link=https://github.com/henrique-coder/streamsnapper/blob/main/LICENSE)
![PyPI - Python Compatible Versions](https://img.shields.io/pypi/pyversions/streamsnapper?style=flat&logo=python&logoColor=blue&color=blue&link=https://pypi.org/project/streamsnapper)

#### Installation (from [PyPI](https://pypi.org/project/streamsnapper))

```bash
pip install -U streamsnapper  # It does not have any features by default, but it can be extended with optional features
pip install -U streamsnapper[downloader]  # It has the feature of downloading online content with support for multiple simultaneous connections
pip install -U streamsnapper[merger]  # It has the feature of merging video files with audio files using FFmpeg (currently it does not need any dependencies)
pip install -U streamsnapper[youtube]  # It has advanced features to extract data from YouTube, with support for several other features
pip install -U streamsnapper[all]  # It has all features available at once
```

### Example Usage

#### `streamsnapper[downloader]`

```python
from streamsnapper import Downloader
from pathlib import Path  # Optional


# A class for downloading direct download URLs.
downloader = Downloader(
    # Initialize the Downloader class with the required settings for downloading a file.
    max_connections='auto',  # The maximum number of connections to use for downloading the file. (default: 'auto')
    overwrite=True,  # Overwrite the file if it already exists. Otherwise, a "_1", "_2", etc. suffix will be added. (default: True)
    show_progress_bar=True,  # Show or hide the download progress bar. (default: True)
    headers=None,  # Custom headers to include in the request. If None, default headers will be used. (default: None)
    timeout=None  # Timeout in seconds for the download process. Or None for no timeout. (default: None)
)

# Downloads a file from the provided URL to the output file path.
# - If the output_path is a directory, the file name will be generated from the server response.
# - If the output_path is a file, the file will be saved with the provided name.
# - If not provided, the file will be saved to the current working directory.
downloader.download(
    url='https://example.com/file',  # The download URL to download the file from. (required)
    output_path=Path.cwd()  # The path to save the downloaded file to. If the path is a directory, the file name will be generated from the server response. If the path is a file, the file will be saved with the provided name. If not provided, the file will be saved to the current working directory. (default: Path.cwd())
)

# All functions are documented and have detailed typings, use your development IDE to learn more.

```

#### `streamsnapper[merger]`

```python
from streamsnapper import Merger


# A class for merging multiple audio and video streams into a single file.
merger = Merger(
    # Initialize the Merger class with the required settings for merging audio and video streams.
    logging=True  # Enable or disable FFmpeg logging. (default: False)
)

# Merge the video and audio streams into a single file.
merger.merge(
    video_path='path/to/video',  # The path to the video file to merge. (required)
    audio_path='path/to/audio',  # The path to the audio file to merge. (required)
    output_path='path/to/output',  # The path to save the output file to. (required)
    ffmpeg_path='local'  # The path to the FFmpeg executable. If 'local', the FFmpeg executable will be searched in the PATH environment variable. (default: 'local')
)

# All functions are documented and have detailed typings, use your development IDE to learn more.

```

#### `streamsnapper[youtube]`

```python
from streamsnapper import YouTube


# YouTube class documentation will be added soon
# ...


from streamsnapper import YouTubeExtractor


# A class for extracting data from YouTube URLs and searching for YouTube videos.
youtube_extractor = YouTubeExtractor(
    # Initialize the Extractor class with some regular expressions for analyzing YouTube URLs.
)

# Identify the platform of a given URL as either YouTube or YouTube Music.
youtube_extractor.identify_platform(
    url='https://music.youtube.com/watch?v=***********'  # The URL to identify the platform from. (required)
)  # --> Returns 'youtube' if the URL corresponds to YouTube, 'youtubeMusic' if it corresponds to YouTube Music. Returns None if the platform is not recognized.

# Extract the YouTube video ID from a URL.
youtube_extractor.extract_video_id(
    url='https://www.youtube.com/watch?v=***********'  # The URL to extract the video ID from. (required)
)  # --> Returns the extracted video ID. If no video ID is found, return None.

# Extract the YouTube playlist ID from a URL.
youtube_extractor.extract_playlist_id(
    url='https://www.youtube.com/playlist?list=**********************************',  # The URL to extract the playlist ID from. (required)
    include_private=False  # Whether to include private playlists, like the mixes YouTube makes for you. (default: False)
)  # --> Returns the extracted playlist ID. If no playlist ID is found or the playlist is private and include_private is False, return None.

# Search for YouTube content based on a query and return a list of URLs (raw data provided by scrapetube library).
youtube_extractor.search(
    query='A cool music name',  # The search query string. (required)
    sort_by='relevance',  # The sorting method to use for the search results. Options are 'relevance', 'upload_date', 'view_count', and 'rating'. (default: 'relevance')
    results_type='video',  # The type of content to search for. Options are 'video', 'channel', 'playlist', and 'movie'. (default: 'video')
    limit=1  # The maximum number of video URLs to return. (default: 1)
)  # --> Returns a list of video URLs from the search results. If no videos are found, returns None.

# Get the video URLs from a YouTube playlist (raw data provided by scrapetube library).
youtube_extractor.get_playlist_videos(
    url='https://www.youtube.com/playlist?list=**********************************',  # The URL of the YouTube playlist. (required)
    limit=None  # The maximum number of video URLs to return. If None, return all video URLs. (default: None)
)  # --> Returns a list of video URLs from the playlist. If no videos are found or the playlist is private, return None.

# Get the video URLs from a YouTube channel (raw data provided by scrapetube library).
# - If channel_id, channel_url, and channel_username are all None, return None.
# - If more than one of channel_id, channel_url, and channel_username is provided, raise ValueError.
youtube_extractor.get_channel_videos(
    channel_id='************************',  # The ID of the YouTube channel. (default: None)
    channel_url='https://www.youtube.com/@********',  # The URL of the YouTube channel. (default: None)
    channel_username='********',  # The username of the YouTube channel. (default: None)
    sort_by='newest',  # The sorting method to use for the channel videos. Options are 'newest', 'oldest', and 'popular' (default: 'newest').
    content_type='videos',  # The type of content to search for. Options are 'videos', 'shorts', and 'streams' (default: 'videos').
    limit=None  # The maximum number of video URLs to return. If None, return all video URLs. (default: None)
)  # --> Returns a list of video URLs from the channel. If no videos are found or the channel is non-existent, return None.

# All functions are documented and have detailed typings, use your development IDE to learn more.

```

### Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, fork the repository and create a pull request. You can also simply open an issue and describe your ideas or report bugs. **Don't forget to give the project a star if you like it!**

1. Fork the project;
2. Create your feature branch ・ `git checkout -b feature/{feature_name}`;
3. Commit your changes ・ `git commit -m "{commit_message}"`;
4. Push to the branch ・ `git push origin feature/{feature_name}`;
5. Open a pull request, describing the changes you made and wait for a review.

### Disclaimer

Please note that downloading copyrighted content from some media services may be illegal in your country. This tool is designed for educational purposes only. Use at your own risk.
