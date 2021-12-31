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
            self.assertTrue(factory.return_value.download_videos.call_args.kwargs['fail_fast'])


class DryRunTests(unittest.TestCase):
    def test_dry_run_extracts_json_without_downloading(self):
        import json
        stdout = io.StringIO()
        with patch('khan_dl.media.MediaDownloader') as factory, contextlib.redirect_stdout(stdout):
            factory.return_value.extract.return_value = {'id': 'abc', 'title': 'Intro'}
            self.assertEqual(main(['--url', 'https://example.org/a', '--dry-run']), 0)
            factory.return_value.download.assert_not_called()
            self.assertEqual(json.loads(stdout.getvalue())['id'], 'abc')


class ResumeReportTests(unittest.TestCase):
    def test_report_preserves_completed_items_on_cancellation(self):
        import json
        from pathlib import Path
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / 'urls.txt'
            report = Path(directory) / 'report.json'
            manifest.write_text(chr(10).join(['https://example.org/a', 'https://example.org/b']))
            with patch('khan_dl.media.MediaDownloader') as factory:
                factory.return_value.download.side_effect = [{'id': 'abc'}, KeyboardInterrupt()]
                self.assertEqual(main(['--batch-file', str(manifest), '--report', str(report), '-q']), 130)
            self.assertEqual(json.loads(report.read_text())['total'], 1)

    def test_empty_queue_is_a_usage_error(self):
        from pathlib import Path
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'empty.txt'
            path.write_text('# no URLs')
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                main(['--batch-file', str(path)])
            self.assertEqual(caught.exception.code, 2)


class FailureIsolationTests(unittest.TestCase):
    def test_dry_run_errors_do_not_abort_later_items(self):
        from pathlib import Path
        import tempfile
        from youtube_dl.utils import DownloadError
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / 'urls.txt'
            manifest.write_text(chr(10).join(['https://example.org/a', 'https://example.org/b']))
            with patch('khan_dl.media.MediaDownloader') as factory, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                factory.return_value.extract.side_effect = [DownloadError('missing'), {'id': 'b'}]
                self.assertEqual(main(['--batch-file', str(manifest), '--dry-run', '-q']), 1)
                self.assertEqual(factory.return_value.extract.call_count, 2)

    def test_course_discovery_failure_is_reported_and_later_courses_continue(self):
        from unittest.mock import MagicMock
        from khan_dl.batch import BatchResult
        from pathlib import Path
        import tempfile
        import json
        first, bad, last = MagicMock(), MagicMock(), MagicMock()
        first.download_videos.return_value = []
        bad.get_course_html.side_effect = ValueError('markup changed')
        last.download_videos.return_value = []
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / 'result.json'
            with patch('khan_dl.interactive_prompt.get_all_course_urls', return_value=['first', 'bad', 'last']) as catalog, patch('khan_dl.khan_downloader.Khan_DL', side_effect=[first, bad, last]), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(['--all', '--report', str(report), '--timeout', '2', '--retries', '0']), 1)
                last.download_videos.assert_called_once()
                catalog.assert_called_once_with(timeout=2, retries=0)
            self.assertEqual(json.loads(report.read_text())['failed'], 1)
