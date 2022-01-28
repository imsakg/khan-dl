import subprocess
import sys
import unittest
from pathlib import Path
import khan_dl


class DistributionTests(unittest.TestCase):
    def test_module_entry_point_supports_help_without_optional_dependencies(self):
        result = subprocess.run([sys.executable, '-S', '-m', 'khan_dl', '--help'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--batch-file', result.stdout)

    def test_release_version_and_setup_metadata_match(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, 'setup.py', '--version'], cwd=str(root),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), khan_dl.__version__)
        self.assertEqual(khan_dl.__version__, '1.1.0')
