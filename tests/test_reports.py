import json
from pathlib import Path
import tempfile
import unittest
from khan_dl.batch import BatchResult
from khan_dl.reports import write_report


class ReportTests(unittest.TestCase):
    def test_serializes_success_failure_and_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'reports' / 'queue.json'
            results = [BatchResult('https://example.org/a', True, 'abc'),
                       BatchResult('https://example.org/b', False, error='offline')]
            write_report(path, results)
            data = json.loads(path.read_text())
            self.assertEqual((data['total'], data['succeeded'], data['failed']), (2, 1, 1))
            self.assertEqual(data['results'][1]['error'], 'offline')
            self.assertEqual(list(path.parent.glob('*.tmp')), [])
