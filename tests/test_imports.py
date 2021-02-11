import subprocess
import sys
import unittest


class ImportTests(unittest.TestCase):
    def test_package_import_does_not_load_optional_dependencies(self):
        code = "import sys, khan_dl; assert 'youtube_dl' not in sys.modules; assert 'requests' not in sys.modules"
        self.assertEqual(subprocess.run([sys.executable, '-c', code]).returncode, 0)
