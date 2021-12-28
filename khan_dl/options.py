"""Immutable configuration shared by CLI, courses and direct downloads."""
from dataclasses import dataclass
import math
import re
from typing import Optional, Tuple


@dataclass(frozen=True)
class DownloadOptions:
    mode: str = 'video'
    output: str = '.'
    format_selector: str = 'bestvideo+bestaudio/best'
    height: Optional[int] = None
    audio_format: str = 'mp3'
    audio_quality: str = '192'
    video_format: Optional[str] = None
    subtitle_languages: Tuple[str, ...] = ()
    automatic_subtitles: bool = False
    subtitle_only: bool = False
    subtitle_format: str = 'best'
    retries: int = 3
    timeout: float = 30.0
    continue_download: bool = True
    overwrite: bool = False
    write_metadata: bool = False
    rate_limit: Optional[int] = None
    archive: Optional[str] = None
    ffmpeg_location: Optional[str] = None
    quiet: bool = False

    def __post_init__(self):
        if not self.output:
            raise ValueError('output directory cannot be empty')
        if not re.fullmatch(r'[0-9]+', self.audio_quality):
            raise ValueError('audio quality must be a nonnegative integer (0-9 quality or kbps)')
        if self.mode == 'audio' and self.video_format is not None:
            raise ValueError('audio extraction and video conversion are mutually exclusive')
        if self.height is not None and self.format_selector != 'bestvideo+bestaudio/best':
            raise ValueError('combine --max-height with the default format, not an explicit --format')
        if self.mode not in ('video', 'audio'):
            raise ValueError('mode must be video or audio')
        if self.retries < 0 or not math.isfinite(self.timeout) or self.timeout <= 0:
            raise ValueError('retries must be nonnegative and timeout positive')
        if self.height is not None and self.height <= 0:
            raise ValueError('height must be positive')
        if self.audio_format not in ('mp3', 'm4a', 'aac', 'flac', 'wav', 'opus', 'vorbis', 'best'):
            raise ValueError('unsupported audio format')
        if self.video_format not in (None, 'mp4', 'mkv', 'webm', 'avi', 'flv', 'ogg'):
            raise ValueError('unsupported video format')
        if self.subtitle_format not in ('best', 'srt', 'vtt', 'ttml'):
            raise ValueError('unsupported subtitle format')
        if self.rate_limit is not None and self.rate_limit <= 0:
            raise ValueError('rate limit must be positive')
        if not self.format_selector.strip():
            raise ValueError('format selector cannot be empty')
