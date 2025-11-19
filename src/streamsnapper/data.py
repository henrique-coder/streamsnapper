"""Data constants and mappings for StreamSnapper."""

# YouTube video format IDs and their corresponding extensions
VIDEO_FORMAT_EXTENSIONS: dict[int, str] = {
    702: "mp4",  # AV1 HFR High - MP4 - 7680x4320
    402: "mp4",  # AV1 HFR - MP4 - 7680x4320
    571: "mp4",  # AV1 HFR - MP4 - 7680x4320
    272: "webm",  # VP9 HFR - WebM - 7680x4320
    138: "mp4",  # H.264 - MP4 - 7680x4320
    701: "mp4",  # AV1 HFR High - MP4 - 3840x2160
    401: "mp4",  # AV1 HFR - MP4 - 3840x2160
    337: "webm",  # VP9.2 HDR HFR - WebM - 3840x2160
    315: "webm",  # VP9 HFR - WebM - 3840x2160
    313: "webm",  # VP9 - WebM - 3840x2160
    305: "mp4",  # H.264 HFR - MP4 - 3840x2160
    266: "mp4",  # H.264 - MP4 - 3840x2160
    700: "mp4",  # AV1 HFR High - MP4 - 2560x1440
    400: "mp4",  # AV1 HFR - MP4 - 2560x1440
    336: "webm",  # VP9.2 HDR HFR - WebM - 2560x1440
    308: "webm",  # VP9 HFR - WebM - 2560x1440
    271: "webm",  # VP9 - WebM - 2560x1440
    304: "mp4",  # H.264 HFR - MP4 - 2560x1440
    264: "mp4",  # H.264 - MP4 - 2560x1440
    699: "mp4",  # AV1 HFR High - MP4 - 1920x1080
    399: "mp4",  # AV1 HFR - MP4 - 1920x1080
    721: "mp4",  # AV1 HFR - MP4 - 1920x1080
    335: "webm",  # VP9.2 HDR HFR - WebM - 1920x1080
    303: "webm",  # VP9 HFR - WebM - 1920x1080
    248: "webm",  # VP9 - WebM - 1920x1080
    # 356: "webm",  # VP9 - WebM - 1920x1080 - YouTube Premium Format (M3U8)
    299: "mp4",  # H.264 HFR - MP4 - 1920x1080
    137: "mp4",  # H.264 - MP4 - 1920x1080
    170: "webm",  # VP8 - WebM - 1920x1080
    698: "mp4",  # AV1 HFR High - MP4 - 1280x720
    398: "mp4",  # AV1 HFR - MP4 - 1280x720
    334: "webm",  # VP9.2 HDR HFR - WebM - 1280x720
    302: "webm",  # VP9 HFR - WebM - 1280x720
    612: "webm",  # VP9 HFR - WebM - 1280x720
    247: "webm",  # VP9 - WebM - 1280x720
    298: "mp4",  # H.264 HFR - MP4 - 1280x720
    136: "mp4",  # H.264 - MP4 - 1280x720
    214: "mp4",  # H.264 - MP4 - 1280x720
    169: "webm",  # VP8 - WebM - 1280x720
    697: "mp4",  # AV1 HFR High - MP4 - 854x480
    397: "mp4",  # AV1 - MP4 - 854x480
    333: "webm",  # VP9.2 HDR HFR - WebM - 854x480
    244: "webm",  # VP9 - WebM - 854x480
    135: "mp4",  # H.264 - MP4 - 854x480
    168: "webm",  # VP8 - WebM - 854x480
    696: "mp4",  # AV1 HFR High - MP4 - 640x360
    396: "mp4",  # AV1 - MP4 - 640x360
    332: "webm",  # VP9.2 HDR HFR - WebM - 640x360
    243: "webm",  # VP9 - WebM - 640x360
    134: "mp4",  # H.264 - MP4 - 640x360
    167: "webm",  # VP8 - WebM - 640x360
    695: "mp4",  # AV1 HFR High - MP4 - 426x240
    395: "mp4",  # AV1 - MP4 - 426x240
    331: "webm",  # VP9.2 HDR HFR - WebM - 426x240
    242: "webm",  # VP9 - WebM - 426x240
    133: "mp4",  # H.264 - MP4 - 426x240
    694: "mp4",  # AV1 HFR High - MP4 - 256x144
    394: "mp4",  # AV1 - MP4 - 256x144
    330: "webm",  # VP9.2 HDR HFR - WebM - 256x144
    278: "webm",  # VP9 - WebM - 256x144
    598: "webm",  # VP9 - WebM - 256x144
    160: "mp4",  # H.264 - MP4 - 256x144
    597: "mp4",  # H.264 - MP4 - 256x144
}

# YouTube audio format IDs and their corresponding extensions
AUDIO_FORMAT_EXTENSIONS: dict[str, str] = {
    "773": "mp4",  # IAMF (Opus) - (VBR) ~900 KBPS - Binaural (7.1.4)
    "338": "webm",  # Opus - (VBR) ~480 KBPS (?) - Ambisonic (4)
    "380": "mp4",  # AC3 - 384 KBPS - Surround (5.1)
    "328": "mp4",  # EAC3 - 384 KBPS - Surround (5.1)
    "325": "mp4",  # DTSE (DTS Express) - 384 KBPS - Surround (5.1)
    "258": "mp4",  # AAC (LC) - 384 KBPS - Surround (5.1)
    "327": "mp4",  # AAC (LC) - 256 KBPS - Surround (5.1)
    "141": "mp4",  # AAC (LC) - 256 KBPS - Stereo (2)
    "774": "webm",  # Opus - (VBR) ~256 KBPS - Stereo (2)
    "256": "mp4",  # AAC (HE v1) - 192 KBPS - Surround (5.1)
    "251": "webm",  # Opus - (VBR) ~128 KBPS - Stereo (2)
    "140": "mp4",  # AAC (LC) - 128 KBPS - Stereo (2)
    "250": "webm",  # Opus - (VBR) ~70 KBPS - Stereo (2)
    "249": "webm",  # Opus - (VBR) ~50 KBPS - Stereo (2)
    "139": "mp4",  # AAC (HE v1) - 48 KBPS - Stereo (2)
    "600": "webm",  # Opus - (VBR) ~35 KBPS - Stereo (2)
    "599": "mp4",  # AAC (HE v1) - 30 KBPS - Stereo (2)
}

# Quality score weights for ranking
QUALITY_WEIGHTS = {
    "bitrate": 10.0,  # Most important for audio quality
    "sample_rate": 0.001,  # Secondary importance
    "channels": 5.0,  # Stereo vs mono preference
    "width": 1.0,  # Video resolution importance
    "height": 1.0,  # Video resolution importance
    "framerate": 1.0,  # Video smoothness
}

# Language code mappings (sample - can be extended)
LANGUAGE_MAPPINGS = {
    "pt": "Portuguese",
    "pt-BR": "Portuguese (Brazil)",
    "en": "English",
    "en-US": "English (United States)",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ru": "Russian",
    "ar": "Arabic",
    "hi": "Hindi",
}

# Default file extensions for different stream types
DEFAULT_EXTENSIONS = {"video": "mp4", "audio": "mp3", "subtitle": "srt"}

# Quality thresholds
QUALITY_THRESHOLDS = {
    "high_quality_audio_bitrate": 128.0,
    "high_quality_audio_sample_rate": 44100,
    "hd_video_height": 720,
    "full_hd_video_height": 1080,
    "ultra_hd_video_height": 2160,
}
