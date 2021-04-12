"""Lazy youtube-dl adapter. Factory injection keeps offline tests deterministic."""
from .options import DownloadOptions


def youtube_dl_factory(options):
    try:
        import youtube_dl
    except ImportError as error:
        raise RuntimeError('Install khan-dl download dependencies (youtube-dl)') from error
    return youtube_dl.YoutubeDL(options)


class MediaDownloader:
    def __init__(self, options=None, backend_factory=None, progress=None):
        self.options = options or DownloadOptions()
        self.backend_factory = backend_factory or youtube_dl_factory
        self.progress = progress

    def backend_options(self):
        return {'noplaylist': True, 'socket_timeout': self.options.timeout,
                'quiet': self.options.quiet}

    def extract(self, url):
        with self.backend_factory(self.backend_options()) as backend:
            return backend.extract_info(url, download=False)
