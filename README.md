<div align="center">

# StreamSnapper

![PyPI - Version](https://img.shields.io/pypi/v/streamsnapper?style=for-the-badge&logo=pypi&logoColor=white&color=0066cc)
![PyPI - Downloads](https://img.shields.io/pypi/dm/streamsnapper?style=for-the-badge&logo=pypi&logoColor=white&color=28a745)
![Python Versions](https://img.shields.io/pypi/pyversions/streamsnapper?style=for-the-badge&logo=python&logoColor=white&color=306998)
![License](https://img.shields.io/pypi/l/streamsnapper?style=for-the-badge&color=blue)

**Extract and analyze YouTube video streams with intelligent quality selection and language fallback**

[🚀 Quick Start](#-quick-start) • [📖 API Reference](#-api-reference) • [💡 Examples](#-examples)

</div>

---

## 🌟 Overview

StreamSnapper extracts YouTube video/audio streams and metadata with intelligent filtering:

- **Quality Selection** - Automatic fallback from preferred to available resolutions
- **Language Priority** - Multi-language fallback with system locale detection
- **Stream Filtering** - HDR, 4K, codec, bitrate, and format filtering
- **Metadata Extraction** - Complete video information, chapters, and statistics

## 🔧 Installation

```bash
# Stable release
uv add --upgrade streamsnapper

# Development version
uv add --upgrade git+https://github.com/henrique-coder/streamsnapper.git --branch main
```

**Requirements:** Python 3.10+

## 🚀 Quick Start

### Basic Usage

```python
from streamsnapper import YouTube

# Extract video data
yt = YouTube()
yt.extract("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

# Analyze streams
yt.analyze_information()
yt.analyze_video_streams("1080p", fallback=True)
yt.analyze_audio_streams(["pt-BR", "en-US", "source"])

# Access results
print(f"Title: {yt.information.title}")
print(f"Best video: {yt.video_streams.best_stream.resolution}")
print(f"Best audio: {yt.audio_streams.best_stream.bitrate}kbps")
```

### Quality Selection

```python
# Specific resolution with fallback
yt.analyze_video_streams("1080p", fallback=True)

# Best or worst quality
yt.analyze_video_streams("best")
yt.analyze_video_streams("worst")

# All streams for manual selection
yt.analyze_video_streams("all")
```

### Language Selection

```python
# Priority list (tries in order, fallback to source)
yt.analyze_audio_streams(["pt-BR", "en-US", "source"])

# System language (fallback to source)
yt.analyze_audio_streams("local")

# Original audio (best quality)
yt.analyze_audio_streams("source")

# All streams
yt.analyze_audio_streams("all")
```

### Private Content

```python
from streamsnapper import YouTube, SupportedCookieBrowser, CookieFile

# Browser cookies
yt = YouTube(cookies=SupportedCookieBrowser.CHROME)

# Cookie file
yt = YouTube(cookies=CookieFile("/path/to/cookies.txt"))
```

## 💡 Examples

### Filter Streams

```python
# Video filtering
videos = yt.video_streams
hd_videos = videos.hd_streams              # ≥720p
h264 = videos.get_by_codec("h264")         # Specific codec
hdr = videos.hdr_streams                   # HDR only
uhd = videos.uhd_streams                   # 4K+

# Audio filtering
audios = yt.audio_streams
hq_audio = audios.high_quality_streams     # ≥128kbps
stereo = audios.stereo_streams             # 2 channels
pt_audio = audios.get_by_language("pt-BR") # Language

# Subtitle filtering
subs = yt.subtitle_streams
manual = subs.manual_subtitles             # Human-created
en_subs = subs.get_by_language("en")       # English
```

### Download Selection

```python
# Get best streams under size limit
videos = [v for v in yt.video_streams.streams if v.size_mb and v.size_mb <= 100]
best_video = max(videos, key=lambda v: v.quality_score)
best_audio = yt.audio_streams.best_stream

print(f"Video: {best_video.url}")
print(f"Audio: {best_audio.url}")
```

### Batch Processing

```python
def process_videos(urls: list[str]) -> list[dict]:
    results = []
    for url in urls:
        yt = YouTube()
        yt.extract(url)
        yt.analyze_information()
        yt.analyze_video_streams("all")

        results.append({
            'title': yt.information.title,
            'duration': yt.information.duration_formatted,
            'qualities': yt.video_streams.available_qualities,
            'has_4k': len(yt.video_streams.uhd_streams) > 0
        })
    return results
```

## 📖 API Reference

### YouTube Class

```python
yt = YouTube(
    logging=False,                # Enable debug logging
    cookies=None                  # Browser or cookie file
)

yt.extract(url: str)              # Extract video data

yt.analyze_information(
    check_thumbnails=False,       # Validate thumbnail URLs
    retrieve_dislike_count=False  # Fetch dislikes from API
)

yt.analyze_video_streams(
    preferred_resolution="all",   # "720p", "1080p", "best", "worst", "all"
    fallback=True                 # Enable resolution fallback
)

yt.analyze_audio_streams(
    preferred_language="all"      # "pt-BR", ["en-US", "source"], "local", "all"
)

yt.analyze_subtitle_streams()     # Extract subtitle information
```

### VideoInformation

```python
info = yt.information

# URLs
info.short_url                    # youtu.be link
info.embed_url                    # Embed URL
info.full_url                     # Full watch URL

# Metadata
info.id                           # Video ID
info.title                        # Title
info.description                  # Description
info.duration                     # Seconds
info.duration_formatted           # HH:MM:SS

# Channel
info.channel_id                   # Channel ID
info.channel_name                 # Channel name
info.is_verified_channel          # Verification status

# Statistics
info.view_count                   # Views
info.like_count                   # Likes
info.comment_count                # Comments
info.upload_date                  # Upload date

# Additional
info.categories                   # Categories list
info.tags                         # Tags list
info.thumbnails                   # Thumbnail URLs
info.chapters                     # Chapter data
```

### VideoStream

```python
stream = yt.video_streams.best_stream

# Quality
stream.resolution                 # "1080p", "720p", etc
stream.width                      # Width in pixels
stream.height                     # Height in pixels
stream.framerate                  # FPS
stream.quality_score              # Ranking score

# Format
stream.codec                      # "h264", "av1", "vp9"
stream.extension                  # "mp4", "webm"
stream.bitrate                    # Bitrate

# Flags
stream.is_hd                      # ≥720p
stream.is_full_hd                 # ≥1080p
stream.is_4k                      # ≥2160p
stream.is_hdr                     # HDR content

# Download
stream.url                        # Direct URL
stream.size                       # Bytes
stream.size_mb                    # Megabytes
```

### VideoStreamCollection

```python
videos = yt.video_streams

# Properties
videos.streams                    # All streams
videos.best_stream                # Highest quality
videos.worst_stream               # Lowest quality
videos.available_qualities        # ["1080p", "720p", ...]
videos.available_codecs           # ["h264", "vp9", ...]

# Filters
videos.hd_streams                 # ≥720p
videos.full_hd_streams            # ≥1080p
videos.uhd_streams                # ≥2160p
videos.hdr_streams                # HDR only

# Methods
videos.get_by_resolution("1080p", fallback=True)
videos.get_by_codec("h264")
videos.get_by_framerate_range(min_fps=60)
videos.get_by_size_range(max_mb=100)
```

### AudioStream

```python
stream = yt.audio_streams.best_stream

# Quality
stream.bitrate                    # Bitrate (kbps)
stream.sample_rate                # Sample rate (Hz)
stream.quality_score              # Ranking score

# Format
stream.codec                      # "aac", "opus"
stream.extension                  # "mp4", "webm"
stream.channels                   # Channel count
stream.channel_description        # "Stereo", "Surround 5.1"

# Language
stream.language                   # Language code
stream.language_name              # Language name

# Flags
stream.is_high_quality            # ≥128kbps
stream.is_lossless_quality        # ≥320kbps & ≥48kHz
stream.is_stereo                  # 2 channels
stream.is_surround                # >2 channels

# Download
stream.url                        # Direct URL
stream.size                       # Bytes
stream.size_mb                    # Megabytes
```

### AudioStreamCollection

```python
audios = yt.audio_streams

# Properties
audios.streams                    # All streams
audios.best_stream                # Highest quality
audios.worst_stream               # Lowest quality
audios.available_languages        # ["en-US", "pt-BR", ...]
audios.available_codecs           # ["aac", "opus", ...]

# Filters
audios.high_quality_streams       # ≥128kbps
audios.lossless_quality_streams   # ≥320kbps & ≥48kHz
audios.stereo_streams             # 2 channels
audios.surround_streams           # >2 channels

# Methods
audios.get_by_language("en-US", fallback=True)
audios.get_by_codec("aac")
audios.get_by_bitrate_range(min_bitrate=128)
audios.get_by_sample_rate_range(min_rate=44100)
```

### SubtitleStream

```python
stream = yt.subtitle_streams.manual_subtitles[0]

# Metadata
stream.language                   # Language code
stream.language_name              # Language name
stream.extension                  # "srt", "vtt"

# Flags
stream.is_manual                  # Human-created
stream.is_auto_generated          # Auto-generated

# Download
stream.url                        # Direct URL
```

### SubtitleStreamCollection

```python
subs = yt.subtitle_streams

# Properties
subs.streams                      # All streams
subs.available_languages          # Language codes
subs.available_language_names     # Language names

# Filters
subs.manual_subtitles             # Human-created only
subs.auto_generated_subtitles     # Auto-generated only

# Methods
subs.get_by_language("en", fallback=True)
```

### YouTubeExtractor

```python
from streamsnapper import YouTubeExtractor

extractor = YouTubeExtractor()

# Extract IDs
video_id = extractor.extract_video_id(url)
playlist_id = extractor.extract_playlist_id(url, include_private=False)

# Identify platform
platform = extractor.identify_platform(url)  # "youtube" or "youtube_music"
```

## 🛡️ Error Handling

```python
from streamsnapper import YouTube, ScrapingError, InvalidDataError

try:
    yt = YouTube()
    yt.extract("https://www.youtube.com/watch?v=invalid")
    yt.analyze_information()
except ScrapingError as e:
    print(f"Extraction failed: {e}")
except InvalidDataError as e:
    print(f"Invalid data: {e}")
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file
