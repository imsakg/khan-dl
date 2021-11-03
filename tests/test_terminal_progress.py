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
