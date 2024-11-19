## StreamSnapper

StreamSnapper is an intuitive library designed to simplify, enhance, and organize media downloads from a variety of audiovisual platforms. It offers efficient, high-speed media extraction with optional tools for extracting data from these platforms.

![PyPI - Version](https://img.shields.io/pypi/v/streamsnapper?style=flat&logo=pypi&logoColor=blue&color=blue)
![PyPI - Downloads](https://img.shields.io/pypi/dm/streamsnapper?style=flat&logo=pypi&logoColor=blue&color=blue)
![PyPI - Status](https://img.shields.io/pypi/status/streamsnapper?style=flat&logo=pypi&logoColor=blue&color=blue)
![PyPI - Format](https://img.shields.io/pypi/format/streamsnapper?style=flat&logo=pypi&logoColor=blue&color=blue)
![PyPI - License](https://img.shields.io/pypi/l/streamsnapper?style=flat&logo=pypi&logoColor=blue&color=blue)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/streamsnapper?style=flat&logo=pypi&logoColor=blue&color=blue)

#### Installation (from PyPI)

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
from streamsnapper import Downloader, DownloadError


# A class for downloading direct download URLs. Created to download YouTube videos and audio streams. However, it can be used to download any direct download URL.
downloader = Downloader(
    # Initialize the Downloader class with the required settings for downloading a file.
    max_connections=4,  # The maximum number of connections (threads) to use for downloading the file. (default: 4)
    show_progress_bar=True,  # Show or hide the download progress bar. (default: True)
    timeout=14400  # The timeout in seconds for the download process. (default: 14400)
)

# Download the file from the provided URL to the output file path.
downloader.download(
    url='YOUR_DOWNLOAD_URL',  # The download URL to download the file from. (required)
    output_file_path=Path.cwd()  # The path to save the downloaded file to. If the path is a directory, the file name will be generated from the server response. If the path is a file, the file will be saved with the provided name. If not provided, the file will be saved to the current working directory. (default: Path.cwd() (from pathlib))
)

# Available attributes
downloader.output_file_path  # The path of the downloaded file (default: None) (str)

# All functions are documented and have detailed typings, use your development IDE to learn more.

```

#### `streamsnapper[merger]`

```python
from streamsnapper import Merger, MergeError


# A class for merging multiple audio and video streams into a single file.
merger = Merger(
    # Initialize the Merger class with the required settings for merging audio and video streams.
    logging=True  # Enable or disable the FFmpeg logging.
)

# Merge the audio and video streams into a single file.
merger.merge(
    video_file_path='YOUR_INPUT_VIDEO_FILE_PATH',  # The path to the video file to merge. (required)
    audio_file_path='YOUR_INPUT_AUDIO_FILE_PATH',  # The path to the audio file to merge. (required)
    output_file_path='YOUR_OUTPUT_MERGED_FILE_PATH',  # The path to save the merged file to. (required)
    ffmpeg_file_path='local'  # The path to the ffmpeg executable. If 'local', the ffmpeg executable will be searched in the PATH environment variable. (default: 'local')
)

# All functions are documented and have detailed typings, use your development IDE to learn more.

```

#### `streamsnapper[youtube]`

```python
from streamsnapper import YouTube, YouTubeExtractor


# ... (YouTube class documentation will be added soon)

# ---

# A class for extracting data from YouTube URLs and searching for YouTube videos.
youtube_extractor = YouTubeExtractor(
    # Initialize the Extractor class with some regular expressions for analyzing YouTube URLs.
)

# Identify the platform of a URL (YouTube or YouTube Music).
youtube_extractor.identify_platform(
    url='YOUR_YOUTUBE_URL'  # The URL to identify the platform from. (required)
)  # --> Return the identified platform. If the platform is not recognized, return None.

# Extract the YouTube video ID from a URL.
youtube_extractor.extract_video_id(
    url='YOUR_YOUTUBE_URL'  # The URL to extract the video ID from. (required)
)  # --> Return the extracted video ID. If no video ID is found, return None.

# Extract the YouTube playlist ID from a URL.
youtube_extractor.extract_playlist_id(
    url='YOUR_YOUTUBE_URL',  # The URL to extract the playlist ID from. (required)
    include_private=False  # Whether to include private playlists, like the mixes YouTube makes for you. (default: False)
)  # --> Return the extracted playlist ID. If no playlist ID is found or the playlist is private, return None.

# Search for YouTube videos, channels, playlists or movies (provided by scrapetube library).
youtube_extractor.search(
    query='YOUR_SEARCH_QUERY',  # The search query to search for. (required)
    sort_by='relevance',  # The sorting method to use for the search results. (default: 'relevance')
    results_type='video',  # The type of results to search for. (default: 'video')
    limit=1  # The maximum number of video URLs to return. (default: 1)
)  # --> Return a list of video URLs from the search results. If no videos are found, return None.

# Get the video URLs from a YouTube playlist (provided by scrapetube library).
youtube_extractor.get_playlist_videos(
    url='YOUR_YOUTUBE_PLAYLIST_URL',  # The URL of the YouTube playlist. (required)
    limit=None  # The maximum number of video URLs to return. If None, return all video URLs. (default: None)
)  # --> Return a list of video URLs from the playlist. If no videos are found or the playlist is private, return None.

# Get the video URLs from a YouTube channel (provided by scrapetube library).
youtube_extractor.get_channel_videos(
    channel_id='YOUR_YOUTUBE_CHANNEL_ID' or None,  # The ID of the YouTube channel. (default: None) ----------------------╲
    channel_url='YOUR_YOUTUBE_CHANNEL_URL' or None,  # The URL of the YouTube channel. (default: None) --------------------〉 You can only put one argument from these three.
    channel_username='YOUR_YOUTUBE_CHANNEL_USERNAME' or None,  # The username of the YouTube channel. (default: None) ----╱
    sort_by='newest',  # The sorting method to use for the channel videos. (default: 'newest')
    content_type='videos',  # The type of videos to get from the channel. (default: 'videos')
    limit=None  # The maximum number of video URLs to return. If None, return all video URLs. (default: None)
)  # --> Return A list of video URLs from the channel. If no videos are found or the channel is non-existent, return None.

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