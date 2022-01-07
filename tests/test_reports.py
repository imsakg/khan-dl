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

    def test_failed_atomic_replace_preserves_previous_report_and_cleans_temp(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.json'
            path.write_text('previous complete report')
            with patch('khan_dl.reports.os.replace', side_effect=OSError('disk error')):
                with self.assertRaises(OSError):
                    write_report(path, [BatchResult('https://example.org/a', True)])
            self.assertEqual(path.read_text(), 'previous complete report')
            self.assertEqual([entry.name for entry in path.parent.iterdir()], ['report.json'])
