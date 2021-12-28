import unittest
from khan_dl.options import DownloadOptions


class OptionTests(unittest.TestCase):
    def test_defaults(self):
        self.assertEqual(DownloadOptions().mode, 'video')
        self.assertEqual(DownloadOptions().format_selector, 'bestvideo+bestaudio/best')

    def test_rejects_invalid_options(self):
        for kwargs in ({'mode': 'gif'}, {'retries': -1}, {'height': 0}, {'timeout': 0},
                       {'audio_format': 'exe'}, {'video_format': 'exe'}, {'subtitle_format': 'foo'}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                DownloadOptions(**kwargs)

    def test_rejects_nonfinite_timeout_invalid_quality_and_conflicts(self):
        for kwargs in ({'timeout': float('nan')}, {'timeout': float('inf')},
                       {'audio_quality': '192k'}, {'audio_quality': '-1'},
                       {'mode': 'audio', 'video_format': 'mp4'},
                       {'height': 720, 'format_selector': 'worst'},
                       {'output': ''}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                DownloadOptions(**kwargs)
