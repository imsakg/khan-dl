import unittest
from khan_dl.progress import ProgressTracker


class ProgressTests(unittest.TestCase):
    def test_unknown_total_and_final_state(self):
        events = []
        tracker = ProgressTracker(events.append)
        tracker({'status': 'downloading', 'downloaded_bytes': 12})
        tracker({'status': 'finished', 'total_bytes': 12, 'downloaded_bytes': 12})
        self.assertIsNone(events[0].percent)
        self.assertEqual(events[1].percent, 100)
        self.assertEqual(tracker.latest.status, 'finished')

    def test_estimated_totals_and_clamping(self):
        tracker = ProgressTracker()
        tracker({'status': 'downloading', 'downloaded_bytes': 200, 'total_bytes_estimate': 100})
        self.assertEqual(tracker.latest.percent, 100)
        tracker({'status': 'downloading', 'downloaded_bytes': -5, 'total_bytes': 0})
        self.assertEqual(tracker.latest.downloaded, 0)
        self.assertIsNone(tracker.latest.percent)
