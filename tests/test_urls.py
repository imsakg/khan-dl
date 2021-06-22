import unittest
from khan_dl.urls import validate_url


class UrlTests(unittest.TestCase):
    def test_accepts_http_media_and_https_courses(self):
        for url in ('http://localhost:8000/clip.mp4', 'https://www.khanacademy.org/math'):
            self.assertEqual(validate_url(url), url)

    def test_rejects_local_protocols_credentials_and_bad_hosts(self):
        for url in ('file:///etc/passwd', 'javascript:alert(1)', 'https:///x',
                    'https://user:secret@example.com', 'https://example.com/\nfoo',
                    'https://example.com:bad/video', ' https://example.com'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_url(url)
