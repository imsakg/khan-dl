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

    def test_metadata_extraction_does_not_download_or_expand_playlists(self):
        info = self.downloader.extract('https://example.org/video')
        backend = self.instances[0]
        self.assertEqual(info['title'], 'Intro')
        self.assertEqual(backend.calls, [('https://example.org/video', False)])
        self.assertTrue(backend.options['noplaylist'])
