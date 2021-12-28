import unittest
from khan_dl.media import MediaDownloader
from khan_dl.options import DownloadOptions


class FakeBackend:
    def __init__(self, options):
        self.options = options
        self.calls = []
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def extract_info(self, url, download):
        self.calls.append((url, download))
        return {'id': 'abc', 'title': 'Intro', 'formats': [{'format_id': '18'}]}


class MediaTests(unittest.TestCase):
    def setUp(self):
        self.instances = []
        def factory(options):
            backend = FakeBackend(options)
            self.instances.append(backend)
            return backend
        self.downloader = MediaDownloader(DownloadOptions(), backend_factory=factory)

    def test_download_selects_video_and_preserves_dynamic_extension(self):
        self.downloader.download('https://example.org/video', title='Intro')
        backend = self.instances[0]
        self.assertEqual(backend.calls[0][1], True)
        self.assertEqual(backend.options['format'], 'bestvideo+bestaudio/best')
        self.assertTrue(backend.options['outtmpl'].endswith('Intro.%(ext)s'))
        self.assertTrue(backend.options['continuedl'])
        self.assertTrue(backend.options['nooverwrites'])

    def test_resolution_cap_keeps_audio_fallback(self):
        options = MediaDownloader(DownloadOptions(height=720)).backend_options()
        self.assertEqual(options['format'], 'bestvideo[height<=720]+bestaudio/best[height<=720]')

    def test_audio_extraction_codec_and_bitrate(self):
        options = MediaDownloader(DownloadOptions(mode='audio', audio_format='flac')).backend_options()
        self.assertEqual(options['format'], 'bestaudio/best')
        self.assertEqual(options['postprocessors'], [{'key': 'FFmpegExtractAudio',
                         'preferredcodec': 'flac', 'preferredquality': '192', 'nopostoverwrites': True}])

    def test_subtitle_languages_and_automatic_caption_opt_in(self):
        options = MediaDownloader(DownloadOptions(subtitle_languages=('en', 'tr'),
                    automatic_subtitles=True, subtitle_format='srt')).backend_options()
        self.assertTrue(options['writesubtitles'])
        self.assertTrue(options['writeautomaticsub'])
        self.assertEqual(options['subtitleslangs'], ['en', 'tr'])
        self.assertEqual(options['subtitlesformat'], 'srt/best')
        self.assertIn({'key': 'FFmpegSubtitlesConvertor', 'format': 'srt'}, options['postprocessors'])
        self.assertFalse(self.downloader.backend_options()['writeautomaticsub'])

    def test_subtitle_only_does_not_download_media(self):
        options = MediaDownloader(DownloadOptions(subtitle_only=True)).backend_options()
        self.assertTrue(options['skip_download'])
        self.assertTrue(options['writesubtitles'])

    def test_video_conversion_uses_ffmpeg_postprocessor(self):
        options = MediaDownloader(DownloadOptions(video_format='mkv', ffmpeg_location='/opt/ffmpeg')).backend_options()
        self.assertEqual(options['postprocessors'], [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mkv'}])
        self.assertEqual(options['ffmpeg_location'], '/opt/ffmpeg')

    def test_retry_reopens_backend_after_transient_network_error(self):
        attempts = []
        outer = self
        class FlakyBackend(FakeBackend):
            def extract_info(self, url, download):
                attempts.append(1)
                if len(attempts) < 3:
                    raise OSError('connection reset')
                return super().extract_info(url, download)
        downloader = MediaDownloader(DownloadOptions(retries=2), backend_factory=FlakyBackend,
                                     sleep=lambda delay: None)
        self.assertEqual(downloader.extract('https://example.org/video')['id'], 'abc')
        self.assertEqual(len(attempts), 3)

    def test_forwards_progress_and_bandwidth_limit(self):
        events = []
        downloader = MediaDownloader(DownloadOptions(rate_limit=2048), progress=events.append)
        options = downloader.backend_options()
        self.assertEqual(options['ratelimit'], 2048)
        options['progress_hooks'][0]({'status': 'finished', 'downloaded_bytes': 20, 'total_bytes': 20})
        self.assertEqual(events[0].percent, 100)

    def test_persistent_archive_and_metadata_sidecars(self):
        options = MediaDownloader(DownloadOptions(archive='archive.txt', write_metadata=True)).backend_options()
        self.assertEqual(options['download_archive'], 'archive.txt')
        self.assertTrue(options['writeinfojson'])

    def test_explicit_audio_selector_is_preserved(self):
        options = MediaDownloader(DownloadOptions(mode='audio', format_selector='worstaudio')).backend_options()
        self.assertEqual(options['format'], 'worstaudio')

    def test_metadata_extraction_does_not_download_or_expand_playlists(self):
        info = self.downloader.extract('https://example.org/video')
        backend = self.instances[0]
        self.assertEqual(info['title'], 'Intro')
        self.assertEqual(backend.calls, [('https://example.org/video', False)])
        self.assertTrue(backend.options['noplaylist'])
