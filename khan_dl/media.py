"""Lazy youtube-dl adapter. Factory injection keeps offline tests deterministic."""
from pathlib import Path
from .options import DownloadOptions
from .paths import output_template


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

    def format_selector(self):
        if self.options.height is not None:
            limit = self.options.height
            return 'bestvideo[height<={0}]+bestaudio/best[height<={0}]'.format(limit)
        return self.options.format_selector

    def backend_options(self):
        return {'noplaylist': True, 'socket_timeout': self.options.timeout,
                'quiet': self.options.quiet, 'format': self.format_selector(),
                'continuedl': self.options.continue_download,
                'nooverwrites': not self.options.overwrite,
                'outtmpl': str(Path(self.options.output)).replace('%', '%%') + '/%(title)s [%(id)s].%(ext)s'}

    def download(self, url, title=None, directory=None):
        options = self.backend_options()
        root = directory or self.options.output
        Path(root).mkdir(parents=True, exist_ok=True)
        if title is not None:
            options['outtmpl'] = output_template(root, title)
        elif directory is not None:
            options['outtmpl'] = str(Path(root)).replace('%', '%%') + '/%(title)s [%(id)s].%(ext)s'
        with self.backend_factory(options) as backend:
            return backend.extract_info(url, download=True)

    def extract(self, url):
        with self.backend_factory(self.backend_options()) as backend:
            return backend.extract_info(url, download=False)
