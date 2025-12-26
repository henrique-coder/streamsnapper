"""Data models for StreamSnapper."""

from .audio import AudioStream, AudioStreamCollection
from .extractor import DownloadPlan, ExtractionMetadata, ExtractionResult, StreamDownloadInfo
from .subtitle import SubtitleStream, SubtitleStreamCollection
from .video import VideoInformation, VideoStream, VideoStreamCollection


__all__ = [
    "AudioStream",
    "AudioStreamCollection",
    "DownloadPlan",
    "ExtractionMetadata",
    "ExtractionResult",
    "StreamDownloadInfo",
    "SubtitleStream",
    "SubtitleStreamCollection",
    "VideoInformation",
    "VideoStream",
    "VideoStreamCollection",
]
