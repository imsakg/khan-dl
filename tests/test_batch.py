import io
import unittest
from khan_dl.batch import read_manifest


class ManifestTests(unittest.TestCase):
    def test_comments_blank_lines_and_stable_deduplication(self):
        text = chr(10).join(['# My queue', 'https://example.org/a', '',
                            'https://example.org/b#t=2', 'https://example.org/a'])
        self.assertEqual(read_manifest(io.StringIO(text)), ['https://example.org/a', 'https://example.org/b#t=2'])

    def test_invalid_line_reports_line_number(self):
        with self.assertRaisesRegex(ValueError, 'line 2'):
            read_manifest(io.StringIO(chr(10).join(['https://example.org/a', 'file:///etc/passwd'])))
