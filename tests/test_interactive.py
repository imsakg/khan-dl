import unittest
from unittest.mock import patch
from bs4 import BeautifulSoup
from khan_dl.interactive_prompt import get_course_urls, get_all_course_urls


class CatalogTests(unittest.TestCase):
    def test_catalog_uses_bounded_fetch_and_deduplicates_courses(self):
        soup = BeautifulSoup('<a class="_1q2jm21" href="/math/algebra">Algebra</a>'
                             '<a class="_1q2jm21" href="/math/algebra">Again</a>', 'html.parser')
        with patch('khan_dl.interactive_prompt.fetch_html', return_value=soup) as fetch:
            self.assertEqual(get_course_urls('/math'), {'Algebra': 'https://www.khanacademy.org/math/algebra'})
            fetch.assert_called_once_with('https://www.khanacademy.org/math')

    def test_all_courses_are_deduplicated_between_domains(self):
        with patch('khan_dl.interactive_prompt.get_course_urls', return_value={'Intro': 'https://www.khanacademy.org/math/a'}):
            self.assertEqual(get_all_course_urls(), ['https://www.khanacademy.org/math/a'])
