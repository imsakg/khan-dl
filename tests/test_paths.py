import unittest
from khan_dl.paths import safe_component, output_template


class PathTests(unittest.TestCase):
    def test_removes_separators_controls_and_template_escape(self):
        name = safe_component('../CON:/bad\\name%')
        for char in '/\\%:':
            self.assertNotIn(char, name)
        self.assertFalse(name.startswith('.'))
        self.assertEqual(safe_component('..'), 'untitled')
        self.assertEqual(safe_component('CON'), '_CON')

    def test_template_keeps_extension_dynamic(self):
        self.assertTrue(output_template('downloads', 'An intro').endswith('An intro.%(ext)s'))

    def test_unicode_and_length(self):
        self.assertEqual(safe_component('İlk ders'), 'İlk ders')
        self.assertLessEqual(len(safe_component('a' * 500).encode('utf-8')), 160)
