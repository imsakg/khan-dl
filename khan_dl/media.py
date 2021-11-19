"""Lazy youtube-dl adapter. Factory injection keeps offline tests deterministic."""
from pathlib import Path
from .options import DownloadOptions
from .paths import output_template
from .urls import validate_url
from .retry import retry_call
from .progress import ProgressTracker
import time


def youtube_dl_factory(options):
    try:
        import youtube_dl
    except ImportError as error:
        raise RuntimeError('Install khan-dl download dependencies (youtube-dl)') from error
    return youtube_dl.YoutubeDL(options)


class MediaDownloader:
    def __init__(self, options=None, backend_factory=None, progress=None, sleep=time.sleep):
        self.options = options or DownloadOptions()
        self.backend_factory = backend_factory or youtube_dl_factory
        self.progress = ProgressTracker(progress)
        self.sleep = sleep

    def format_selector(self):
        if self.options.mode == 'audio':
            return 'bestaudio/best'
        if self.options.height is not None:
            limit = self.options.height
            return 'bestvideo[height<={0}]+bestaudio/best[height<={0}]'.format(limit)
        return self.options.format_selector

    def backend_options(self):
        result = {'progress_hooks': [self.progress], 'ratelimit': self.options.rate_limit,
                  'retries': 0, 'fragment_retries': self.options.retries, 'noplaylist': True, 'socket_timeout': self.options.timeout,
                'quiet': self.options.quiet, 'format': self.format_selector(),
                'continuedl': self.options.continue_download,
                'nooverwrites': not self.options.overwrite,
                'outtmpl': str(Path(self.options.output)).replace('%', '%%') + '/%(title)s [%(id)s].%(ext)s'}
        result.update(download_archive=self.options.archive,
                      writeinfojson=self.options.write_metadata)
        result.update(skip_download=self.options.subtitle_only,
                      writesubtitles=bool(self.options.subtitle_languages) or self.options.subtitle_only,
                      writeautomaticsub=self.options.automatic_subtitles,
                      subtitleslangs=list(self.options.subtitle_languages) or None,
                      subtitlesformat=self.options.subtitle_format if self.options.subtitle_format == 'best' else self.options.subtitle_format + '/best')
        if self.options.mode == 'audio':
            result['postprocessors'] = [{'key': 'FFmpegExtractAudio',
                'preferredcodec': self.options.audio_format,
                'preferredquality': self.options.audio_quality}]
        if self.options.video_format and self.options.mode == 'video':
            result['postprocessors'] = [{'key': 'FFmpegVideoConvertor',
                                        'preferedformat': self.options.video_format}]
        if self.options.subtitle_format != 'best' and (self.options.subtitle_languages or self.options.subtitle_only or self.options.automatic_subtitles):
            result.setdefault('postprocessors', []).append(
                {'key': 'FFmpegSubtitlesConvertor', 'format': self.options.subtitle_format})
        if self.options.ffmpeg_location:
            result['ffmpeg_location'] = self.options.ffmpeg_location
        return result

    def download(self, url, title=None, directory=None):
        options = self.backend_options()
        root = directory or self.options.output
        Path(root).mkdir(parents=True, exist_ok=True)
        if title is not None:
            options['outtmpl'] = output_template(root, title)
        elif directory is not None:
            options['outtmpl'] = str(Path(root)).replace('%', '%%') + '/%(title)s [%(id)s].%(ext)s'
        return self._extract(url, options, download=True)

    def extract(self, url):
        return self._extract(url, self.backend_options(), download=False)

    def _extract(self, url, options, download):
        validate_url(url)
        from youtube_dl.utils import DownloadError
        def operation():
            with self.backend_factory(options) as backend:
                info = backend.extract_info(url, download=download)
                if info is None:
                    raise ValueError('extractor returned no media information')
                return info
        return retry_call(operation, retries=self.options.retries,
                          exceptions=(OSError, DownloadError), sleep=self.sleep)
