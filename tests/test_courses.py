import unittest
from bs4 import BeautifulSoup
from khan_dl.courses import extract_video_ids, parse_units, course_title


class CourseParsingTests(unittest.TestCase):
    def test_stable_video_id_extraction_handles_json_spacing(self):
        html = chr(10).join(['{"youtubeId": "abcdefghijk"}', '{"youtubeId":"abcdefghijk"}',
                             '{"youtubeId":"ABCDEFGHIJK"}', '{"youtubeId":"short"}'])
        self.assertEqual(extract_video_ids(html), ['abcdefghijk', 'ABCDEFGHIJK'])

    def test_units_are_same_site_and_deduplicated(self):
        soup = BeautifulSoup('<a data-test-id="unit-header" href="/math/unit">Unit: One</a>'
                             '<a data-test-id="unit-header" href="/math/unit">Again</a>', 'html.parser')
        units = parse_units(soup, 'https://www.khanacademy.org/math/course')
        self.assertEqual(units, [('Unit: One', 'https://www.khanacademy.org/math/unit')])

    def test_external_unit_links_are_rejected(self):
        soup = BeautifulSoup('<a data-test-id="unit-header" href="//evil.example/unit">Bad</a>', 'html.parser')
        with self.assertRaises(ValueError):
            parse_units(soup, 'https://www.khanacademy.org/math')

    def test_missing_units_explains_markup_drift(self):
        with self.assertRaisesRegex(ValueError, 'unit'):
            parse_units(BeautifulSoup('<html></html>', 'html.parser'), 'https://www.khanacademy.org/math')

    def test_title_falls_back_without_crashing(self):
        self.assertEqual(course_title(BeautifulSoup('<title>Math</title>', 'html.parser')), 'Math')
