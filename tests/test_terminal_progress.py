import io
import unittest
from khan_dl.progress import ProgressTracker, TerminalProgress


class TerminalProgressTests(unittest.TestCase):
    def test_unknown_size_and_finished_event_render_without_ansi(self):
        stream = io.StringIO()
        tracker = ProgressTracker(TerminalProgress(stream=stream, interval=0))
        tracker({'status': 'downloading', 'downloaded_bytes': 12, 'filename': 'lesson.mp4'})
        tracker({'status': 'finished', 'downloaded_bytes': 20, 'total_bytes': 20})
        self.assertIn('12 bytes', stream.getvalue())
        self.assertIn('100.0%', stream.getvalue())
        self.assertNotIn(chr(27), stream.getvalue())

    def test_throttle_always_allows_finished_event(self):
        stream = io.StringIO()
        times = iter([1, 1.1, 1.2])
        tracker = ProgressTracker(TerminalProgress(stream, interval=1, clock=lambda: next(times)))
        tracker({'status': 'downloading', 'downloaded_bytes': 1})
        tracker({'status': 'downloading', 'downloaded_bytes': 2})
        tracker({'status': 'finished', 'downloaded_bytes': 3, 'total_bytes': 3})
        self.assertEqual(len(stream.getvalue().splitlines()), 2)
        self.assertIn('finished', stream.getvalue())
