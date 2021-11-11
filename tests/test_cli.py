import contextlib
import io
import unittest
from unittest.mock import patch
from khan_dl.cli import build_parser, options_from_args, main


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


class CommandTests(unittest.TestCase):
    def test_direct_url_uses_batch_runner_and_returns_success(self):
        with patch('khan_dl.media.MediaDownloader') as factory, contextlib.redirect_stderr(io.StringIO()):
            factory.return_value.download.return_value = {'id': 'abc'}
            self.assertEqual(main(['--url', 'https://example.org/a', '--quiet']), 0)
            factory.return_value.download.assert_called_once_with('https://example.org/a')

    def test_invalid_options_exit_as_usage_error(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            main(['--url', 'https://example.org/a', '--retries', '-1'])
        self.assertEqual(caught.exception.code, 2)


class CourseCommandTests(unittest.TestCase):
    def test_course_receives_shared_options_and_fail_fast(self):
        with patch('khan_dl.khan_downloader.Khan_DL') as factory, contextlib.redirect_stderr(io.StringIO()):
            factory.return_value.download_videos.return_value = []
            self.assertEqual(main(['-c', 'https://www.khanacademy.org/math/course',
                                   '-o', 'lessons', '-x', '--fail-fast']), 0)
            self.assertEqual(factory.call_args.args[0], 'lessons')
            self.assertEqual(factory.call_args.kwargs['options'].mode, 'audio')
            factory.return_value.download_videos.assert_called_once_with(fail_fast=True)


class DryRunTests(unittest.TestCase):
    def test_dry_run_extracts_json_without_downloading(self):
        import json
        stdout = io.StringIO()
        with patch('khan_dl.media.MediaDownloader') as factory, contextlib.redirect_stdout(stdout):
            factory.return_value.extract.return_value = {'id': 'abc', 'title': 'Intro'}
            self.assertEqual(main(['--url', 'https://example.org/a', '--dry-run']), 0)
            factory.return_value.download.assert_not_called()
            self.assertEqual(json.loads(stdout.getvalue())['id'], 'abc')
