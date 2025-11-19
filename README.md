<div align="center">

# StreamSnapper

![PyPI - Version](https://img.shields.io/pypi/v/streamsnapper?style=for-the-badge&logo=pypi&logoColor=white&color=0066cc)
![PyPI - Downloads](https://img.shields.io/pypi/dm/streamsnapper?style=for-the-badge&logo=pypi&logoColor=white&color=28a745)
![Python Versions](https://img.shields.io/pypi/pyversions/streamsnapper?style=for-the-badge&logo=python&logoColor=white&color=306998)
![License](https://img.shields.io/pypi/l/streamsnapper?style=for-the-badge&color=blue)

**Smart YouTube Stream Processor with Type-Safe Data Models**

_Extract, analyze, and organize YouTube content with automatic validation and modern Python patterns_

[🚀 Quick Start](#-quick-start) • [📖 Documentation](#-documentation) • [⚡ Features](#-features)

</div>

---

## 🌟 Overview

StreamSnapper is a modern Python library for YouTube content extraction with:

- **Type-Safe Models** - Built with Pydantic v2 for automatic validation
- **Smart Selection** - Intelligent quality and language fallback
- **Rich Collections** - Powerful filtering and sorting methods
- **Production Ready** - Clean API, comprehensive error handling

## 🔧 Installation

### Using UV (Recommended)

```bash
# Stable version
uv add --upgrade streamsnapper

# Active development version
uv add --upgrade git+https://github.com/henrique-coder/streamsnapper.git --branch main
```

### Requirements

- Python 3.10 or higher
- Dependencies installed automatically

## 🚀 Quick Start

### Basic Example

```python
from streamsnapper import YouTube

# Initialize and extract
youtube = YouTube()
youtube.extract("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Analyze content
youtube.analyze_information()
youtube.analyze_video_streams("1080p", fallback=True)
youtube.analyze_audio_streams(["en-US", "source"])

# Access data
print(f"📺 {youtube.information.title}")
print(f"👀 {youtube.information.view_count:,} views")
print(f"🎬 {len(youtube.video_streams)} video streams available")
```

### Getting Best Quality Streams

```python
from streamsnapper import YouTube

youtube = YouTube()
youtube.extract("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Get best quality
youtube.analyze_video_streams("best")
youtube.analyze_audio_streams("all")

# Access best streams
best_video = youtube.video_streams.best_stream
best_audio = youtube.audio_streams.best_stream

print(f"Video: {best_video.resolution} {best_video.codec}")
print(f"Audio: {best_audio.bitrate}kbps {best_audio.codec}")
```

### Using Cookies for Private Content

```python
from streamsnapper import YouTube, SupportedCookieBrowser, CookieFile

# Use browser cookies
youtube = YouTube(cookies=SupportedCookieBrowser.CHROME)

# Or use cookie file
youtube = YouTube(cookies=CookieFile("/path/to/cookies.txt"))

# Extract private/restricted content
youtube.extract("https://www.youtube.com/watch?v=private_video")
youtube.analyze_information()
```

## ⚡ Features

### 🔍 Smart Stream Selection

```python
# Resolution preferences with fallback
youtube.analyze_video_streams("1080p", fallback=True)

# Language priority list with source fallback
# Tries each language in order, then falls back to source if none match
youtube.analyze_audio_streams(["pt-BR", "en-US", "source"])

# System language detection with intelligent fallback
# String: Falls back to source if system language not found
youtube.analyze_audio_streams("local")

# List with local: Tries system language, then continues to next languages
youtube.analyze_audio_streams(["local", "en-US", "source"])

# Direct to source: Always gets original video audio (best quality)
youtube.analyze_audio_streams("source")
```

### 📊 Advanced Filtering

```python
# Video streams
videos = youtube.video_streams
hd_videos = videos.hd_streams              # HD quality only
h264_streams = videos.get_by_codec("h264") # Specific codec
hdr_streams = videos.hdr_streams           # HDR content

# Audio streams
audios = youtube.audio_streams
high_quality = audios.high_quality_streams  # ≥128kbps
stereo = audios.stereo_streams             # Stereo only
english = audios.get_by_language("en-US")  # Language filter

# Subtitles
subtitles = youtube.subtitle_streams
manual = subtitles.manual_subtitles        # Human-created
english_subs = subtitles.get_by_language("en")
```

### 📈 Quality Analysis

```python
# Video quality metrics
video = youtube.video_streams.best_stream
print(f"Resolution: {video.resolution}")
print(f"Quality Score: {video.quality_score}")
print(f"Codec: {video.codec}")
print(f"HDR: {video.is_hdr}")
print(f"4K: {video.is_4k}")

# Audio quality metrics
audio = youtube.audio_streams.best_stream
print(f"Bitrate: {audio.bitrate}kbps")
print(f"Sample Rate: {audio.sample_rate}Hz")
print(f"Channels: {audio.channel_description}")
print(f"Quality Score: {audio.quality_score}")
```

## 📖 Documentation

### Core Classes

#### `YouTube`

Main class for extracting and analyzing YouTube content.

```python
youtube = YouTube(
    logging=True,                    # Enable logging
    cookies=SupportedCookieBrowser.CHROME  # Browser cookies
)

# Extract video
youtube.extract(url: str)

# Analyze content
youtube.analyze_information(
    check_thumbnails=True,           # Validate thumbnails
    retrieve_dislike_count=True      # Get dislikes from API
)

youtube.analyze_video_streams(
    preferred_resolution="1080p",    # Target resolution
    fallback=True                    # Enable fallback
)

youtube.analyze_audio_streams(
    preferred_language=["pt-BR", "en-US", "source"]  # Language priority with fallback
)

youtube.analyze_subtitle_streams()
```

#### `YouTubeExtractor`

Advanced URL analysis and content extraction utilities.

```python
from streamsnapper import YouTubeExtractor

extractor = YouTubeExtractor()

# Extract IDs
video_id = extractor.extract_video_id(url)
playlist_id = extractor.extract_playlist_id(url)

# Identify platform
platform = extractor.identify_platform(url)  # 'youtube' or 'youtube_music'

# Search content
results = extractor.search(
    query="search term",
    sort_by="relevance",
    results_type="video",
    limit=10
)

# Get playlist videos
videos = extractor.get_playlist_videos(url, limit=50)

# Get channel content
videos = extractor.get_channel_videos(
    channel_id="UCxxxxxx",
    sort_by="newest",
    content_type="videos"
)
```

### Data Models

#### `VideoInformation`

Complete video metadata with automatic validation.

```python
info = youtube.information

# URLs
info.short_url           # youtu.be link
info.embed_url           # Embed URL
info.youtube_music_url   # YouTube Music URL

# Basic info
info.id                  # Video ID
info.title               # Video title
info.description         # Description
info.duration            # Duration in seconds
info.duration_formatted  # HH:MM:SS format

# Channel info
info.channel_id          # Channel ID
info.channel_name        # Channel name
info.channel_url         # Channel URL
info.is_verified_channel # Verification status

# Statistics
info.view_count          # Views
info.like_count          # Likes
info.dislike_count       # Dislikes (if enabled)
info.comment_count       # Comments

# Metadata
info.upload_date         # Upload date
info.categories          # Categories list
info.tags                # Tags list
info.thumbnails          # Thumbnail URLs
info.chapters            # Chapter information
```

#### `VideoStream`

Individual video stream with quality metrics.

```python
stream = youtube.video_streams.best_stream

# Quality info
stream.resolution        # e.g., "1080p"
stream.width            # Width in pixels
stream.height           # Height in pixels
stream.framerate        # FPS
stream.quality_score    # Quality ranking score
stream.aspect_ratio     # Aspect ratio (e.g., 1.78 for 16:9)

# Format info
stream.codec            # Video codec (e.g., "h264")
stream.codec_variant    # Codec variant
stream.extension        # File extension
stream.bitrate          # Bitrate

# Flags
stream.is_hd            # HD quality (≥720p)
stream.is_full_hd       # Full HD (≥1080p)
stream.is_4k            # 4K quality (≥2160p)
stream.is_hdr           # HDR content

# Download info
stream.url              # Direct URL
stream.size             # File size in bytes
stream.size_mb          # File size in MB
```

#### `VideoStreamCollection`

Collection of video streams with filtering methods.

```python
videos = youtube.video_streams

# Properties
videos.streams                # All streams
videos.best_stream           # Highest quality
videos.worst_stream          # Lowest quality
videos.has_streams           # Has any streams
videos.available_qualities   # List of resolutions
videos.available_codecs      # List of codecs

# Filtering
videos.hd_streams            # HD (≥720p)
videos.full_hd_streams       # Full HD (≥1080p)
videos.uhd_streams           # 4K+ (≥2160p)
videos.hdr_streams           # HDR content

# Methods
videos.get_by_resolution("1080p", fallback=True)
videos.get_by_codec("h264")
videos.get_by_framerate_range(min_fps=60)
videos.get_by_size_range(max_mb=100)
```

#### `AudioStream`

Individual audio stream with quality metrics.

```python
stream = youtube.audio_streams.best_stream

# Quality info
stream.bitrate              # Bitrate in kbps
stream.sample_rate          # Sample rate in Hz
stream.quality_score        # Quality ranking score

# Format info
stream.codec                # Audio codec (e.g., "aac")
stream.codec_variant        # Codec variant
stream.extension            # File extension
stream.channels             # Number of channels
stream.channel_description  # e.g., "Stereo", "Surround 5.1"

# Language
stream.language             # Language code
stream.language_name        # Language name

# Quality flags
stream.is_high_quality      # ≥128kbps
stream.is_lossless_quality  # ≥320kbps & ≥48kHz
stream.is_stereo            # 2 channels
stream.is_surround          # >2 channels

# Download info
stream.url                  # Direct URL
stream.size                 # File size in bytes
stream.size_mb              # File size in MB
```

#### `AudioStreamCollection`

Collection of audio streams with filtering methods.

```python
audios = youtube.audio_streams

# Properties
audios.streams                # All streams
audios.best_stream           # Highest quality
audios.worst_stream          # Lowest quality
audios.has_streams           # Has any streams
audios.available_languages   # List of languages
audios.available_codecs      # List of codecs

# Filtering
audios.high_quality_streams   # ≥128kbps
audios.lossless_quality_streams  # ≥320kbps & ≥48kHz
audios.stereo_streams        # Stereo only
audios.surround_streams      # Surround sound

# Methods
audios.get_by_language("en-US", fallback=True)
audios.get_by_codec("aac")
audios.get_by_bitrate_range(min_bitrate=128)
audios.get_by_sample_rate_range(min_rate=44100)
```

#### `SubtitleStream`

Individual subtitle stream with metadata.

```python
stream = youtube.subtitle_streams.manual_subtitles[0]

# Basic info
stream.language             # Language code
stream.language_name        # Language name
stream.extension            # Format (e.g., "vtt", "srt")
stream.format_name          # Format name

# Flags
stream.is_manual            # Human-created
stream.is_auto_generated    # Auto-generated
stream.is_translatable      # Can be translated

# Quality
stream.quality_score        # Quality ranking

# Download
stream.url                  # Direct URL
```

#### `SubtitleStreamCollection`

Collection of subtitle streams with filtering methods.

```python
subtitles = youtube.subtitle_streams

# Properties
subtitles.streams                  # All streams
subtitles.has_streams              # Has any streams
subtitles.available_languages      # Language codes
subtitles.available_language_names # Language names
subtitles.available_extensions     # Available formats

# Filtering
subtitles.manual_subtitles         # Human-created
subtitles.auto_generated_subtitles # Auto-generated

# Methods
subtitles.get_by_language("en")
subtitles.get_by_extension("vtt")
subtitles.get_best_for_language("en")
```

### Export & Conversion

Convert Pydantic models to different formats:

```python
# To dictionary
info_dict = youtube.information.to_dict()
video_dict = youtube.video_streams.to_dict()
audio_dict = youtube.audio_streams.to_dict()

# To JSON string
info_json = youtube.information.to_json()
video_json = youtube.video_streams.to_json()
audio_json = youtube.audio_streams.to_json()

# Individual streams
best_video = youtube.video_streams.best_stream
if best_video:
    video_data = best_video.to_dict()
```

## 🎯 Advanced Examples

### Multi-Video Analysis

```python
from streamsnapper import YouTube

def analyze_multiple_videos(urls: list[str]) -> list[dict]:
    results = []

    for url in urls:
        youtube = YouTube()
        youtube.extract(url)
        youtube.analyze_information()
        youtube.analyze_video_streams("all")
        youtube.analyze_audio_streams("all")

        results.append({
            'title': youtube.information.title,
            'duration': youtube.information.duration_formatted,
            'views': youtube.information.view_count,
            'qualities': youtube.video_streams.available_qualities,
            'has_4k': len(youtube.video_streams.uhd_streams) > 0
        })

    return results
```

### Custom Quality Selection

```python
from streamsnapper import YouTube

def select_optimal_streams(url: str, max_size_mb: int = 100):
    youtube = YouTube()
    youtube.extract(url)
    youtube.analyze_video_streams("all")
    youtube.analyze_audio_streams("all")

    # Filter by size
    suitable_videos = [
        s for s in youtube.video_streams.streams
        if s.size_mb and s.size_mb <= max_size_mb
    ]

    # Get best within size limit
    best_video = max(suitable_videos, key=lambda s: s.quality_score)

    # Get best audio
    best_audio = youtube.audio_streams.best_stream

    return best_video, best_audio
```

### Multi-Language Content

```python
from streamsnapper import YouTube

def analyze_languages(url: str):
    youtube = YouTube()
    youtube.extract(url)
    youtube.analyze_audio_streams("all")
    youtube.analyze_subtitle_streams()

    # Audio languages
    audio_langs = youtube.audio_streams.available_languages

    # Subtitle languages
    sub_langs = youtube.subtitle_streams.available_languages

    # Analysis per language
    analysis = {}
    for lang in audio_langs:
        audio = youtube.audio_streams.get_by_language(lang)
        subs = youtube.subtitle_streams.get_by_language(lang)

        analysis[lang] = {
            'audio_quality': audio[0].quality_score if audio else 0,
            'has_manual_subs': any(s.is_manual for s in subs),
            'subtitle_count': len(subs)
        }

    return analysis
```

## 🛡️ Error Handling

```python
from streamsnapper import YouTube, ScrapingError, InvalidDataError

try:
    youtube = YouTube()
    youtube.extract("https://www.youtube.com/watch?v=example")
    youtube.analyze_information()
except ScrapingError as e:
    print(f"Failed to extract video: {e}")
except InvalidDataError as e:
    print(f"Invalid data received: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following coding standards
4. Test your changes: `python -m pytest`
5. Commit: `git commit -m "Add amazing feature"`
6. Push: `git push origin feature/amazing-feature`
7. Create a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

StreamSnapper is designed for **educational purposes**, **research projects**, **personal use**, and **development**. Please respect content creators and copyright laws. Use responsibly and in accordance with YouTube's Terms of Service.

---

<div align="center">

**⭐ Star us on GitHub — it helps a lot!**

[🐛 Report Bug](https://github.com/henrique-coder/streamsnapper/issues) •
[✨ Request Feature](https://github.com/henrique-coder/streamsnapper/issues) •
[💬 Discussions](https://github.com/henrique-coder/streamsnapper/discussions)

Made with ❤️ by [henrique-coder](https://github.com/henrique-coder)

</div>
