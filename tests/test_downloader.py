from pathlib import Path
import tempfile
import unittest
from bs4 import BeautifulSoup
from khan_dl.khan_downloader import Khan_DL
from khan_dl.options import DownloadOptions


class DownloaderTests(unittest.TestCase):
    def test_course_pipeline_preserves_root_and_delegates_extractor_titles(self):
        root = 'https://www.khanacademy.org/math/course'
        pages = {root: '<h1 data-test-id="unit-block-title">Math: Intro</h1>'
                       '<a data-test-id="unit-header" href="/math/unit">Unit/One</a>',
                 'https://www.khanacademy.org/math/unit': '<script>{"youtubeId":"abcdefghijk"}</script>'}
        calls = []
        def fetch(url, **kwargs):
            calls.append(kwargs)
            return BeautifulSoup(pages[url], 'html.parser')
        class Media:
            def download(self, url, directory):
                calls.append((url, directory))
                return {'id': 'abcdefghijk'}
        with tempfile.TemporaryDirectory() as output:
            course = Khan_DL(output, root, options=DownloadOptions(timeout=7), page_fetcher=fetch)
            course.get_course_html()
            course.generate_unit_slugs()
            course.generate_unit_urls()
            course.generate_course_slugs_video_ids()
            results = course.download_videos(downloader=Media())
            self.assertTrue(results[0].success)
            self.assertEqual(course.output_rel_path, str(Path(output).resolve()))
            self.assertEqual(course.youtube_id_list, ['abcdefghijk'])
            self.assertEqual(calls[0]['timeout'], 7)
            self.assertEqual(calls[-1][0], 'https://www.youtube.com/watch?v=abcdefghijk')
            self.assertTrue(calls[-1][1].startswith(str(Path(output).resolve())))
            self.assertIn('Unit_One', calls[-1][1])

    def test_course_root_must_belong_to_khan_academy(self):
        with self.assertRaises(ValueError):
            Khan_DL('.', 'https://example.org/math')
