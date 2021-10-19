import contextlib
import io
import unittest
from khan_dl.cli import build_parser, options_from_args


class ParserTests(unittest.TestCase):
    def test_parses_media_options_into_shared_configuration(self):
        args = build_parser().parse_args(['--url', 'https://example.org/a', '-x',
                   '--audio-format', 'flac', '--sub-langs', 'en,tr', '--max-height', '720',
                   '--retries', '2', '--timeout', '9', '--output', 'lessons'])
        options = options_from_args(args)
        self.assertEqual((options.mode, options.audio_format), ('audio', 'flac'))
        self.assertEqual(options.subtitle_languages, ('en', 'tr'))
        self.assertEqual((options.retries, options.timeout, options.output), (2, 9, 'lessons'))

    def test_sources_are_mutually_exclusive(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            build_parser().parse_args(['--url', 'https://example.org/a', '--all'])
