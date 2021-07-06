import io
import unittest
from khan_dl.batch import read_manifest, BatchRunner


class ManifestTests(unittest.TestCase):
    def test_comments_blank_lines_and_stable_deduplication(self):
        text = chr(10).join(['# My queue', 'https://example.org/a', '',
                            'https://example.org/b#t=2', 'https://example.org/a'])
        self.assertEqual(read_manifest(io.StringIO(text)), ['https://example.org/a', 'https://example.org/b#t=2'])

    def test_invalid_line_reports_line_number(self):
        with self.assertRaisesRegex(ValueError, 'line 2'):
            read_manifest(io.StringIO(chr(10).join(['https://example.org/a', 'file:///etc/passwd'])))


class BatchTests(unittest.TestCase):
    def test_continues_after_failure_and_reports_ordered_results(self):
        class Downloader:
            def download(self, url):
                if url.endswith('/bad'):
                    raise ValueError('unavailable')
                return {'id': 'ok'}
        result = BatchRunner(Downloader()).run(['https://example.org/bad', 'https://example.org/good'])
        self.assertEqual([entry.success for entry in result], [False, True])
        self.assertEqual(result[0].error, 'unavailable')
        self.assertEqual(result[1].media_id, 'ok')

    def test_fail_fast_stops_after_first_error(self):
        class Downloader:
            def download(self, url):
                raise ValueError('bad')
        self.assertEqual(len(BatchRunner(Downloader(), fail_fast=True).run(['x', 'y'])), 1)

    def test_keyboard_interrupt_is_not_swallowed(self):
        class Downloader:
            def download(self, url):
                raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            BatchRunner(Downloader()).run(['x'])
