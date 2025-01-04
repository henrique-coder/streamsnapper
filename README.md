## StreamSnapper

![PyPI - Version](https://img.shields.io/pypi/v/streamsnapper?style=flat&logo=pypi&logoColor=blue&color=blue&link=https://pypi.org/project/streamsnapper)
![PyPI - Downloads](https://img.shields.io/pypi/dm/streamsnapper?style=flat&logo=pypi&logoColor=blue&color=blue&link=https://pypi.org/project/streamsnapper)
![PyPI - Code Style](https://img.shields.io/badge/code%20style-ruff-blue?style=flat&logo=ruff&logoColor=blue&color=blue&link=https://github.com/astral-sh/ruff)
![PyPI - Format](https://img.shields.io/pypi/format/streamsnapper?style=flat&logo=pypi&logoColor=blue&color=blue&link=https://pypi.org/project/streamsnapper)
![PyPI - Python Compatible Versions](https://img.shields.io/pypi/pyversions/streamsnapper?style=flat&logo=python&logoColor=blue&color=blue&link=https://pypi.org/project/streamsnapper)

StreamSnapper is an intuitive library designed to simplify, improve, and organize YouTube and Youtube Music media streams. It offers scraping functions with higher speed extraction and efficiency with the latest tools to perform such processes.

#### Installation (from [PyPI](https://pypi.org/project/streamsnapper))

```bash
pip install -U streamsnapper
```

### Example Usage

```python
from streamsnapper import YouTube


youtube = YouTube(logging=False)

youtube.extract(url="https://www.youtube.com/watch?v=***********", ytdlp_data=None)
youtube.analyze(check_thumbnails=False, retrieve_dislike_count=False)
youtube.analyze_video_streams(preferred_quality="all")
youtube.analyze_audio_streams(preferred_language="local")
youtube.analyze_subtitle_streams()

youtube.download(
    video_stream=None,
    audio_stream=None,
    output_path="path/to/file",
    ffmpeg_path="local",
    pre_allocate_space=False,
    use_ram_buffer=True,
    max_connections="auto",
    connection_speed=80,
    overwrite=True,
    show_progress_bar=True,
    timeout=None,
    logging=False,
)


from streamsnapper import YouTubeExtractor


youtube_extractor = YouTubeExtractor()

print(youtube_extractor.identify_platform(url="https://music.youtube.com/watch?v=***********"))

print(youtube_extractor.extract_video_id(url="https://www.youtube.com/watch?v=***********"))

print(
    youtube_extractor.extract_playlist_id(
        url="https://www.youtube.com/playlist?list=**********************************", include_private=False
    )
)

print(youtube_extractor.search(query="A cool music name", sort_by="relevance", results_type="video", limit=1))

print(
    youtube_extractor.get_playlist_videos(
        url="https://www.youtube.com/playlist?list=**********************************", limit=None
    )
)

print(
    youtube_extractor.get_channel_videos(
        channel_id="************************",
        channel_url="https://www.youtube.com/@********",
        channel_username="********",
        sort_by="newest",
        content_type="videos",
        limit=None,
    )
)

# All functions are documented and have detailed typings, use your development IDE to learn more.

```

```python
from streamsnapper import Merger


merger = Merger(
    logging=False
)

merger.merge(
    video_path='path/to/video',
    audio_path='path/to/audio',
    output_path='path/to/output',
    ffmpeg_path='local'
)

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
