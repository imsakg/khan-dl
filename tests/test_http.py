import unittest
import requests
from khan_dl.http import fetch_html


class Response:
    def __init__(self, status=200):
        self.status_code = status
        self.text = '<h1>Course</h1>'
        self.closed = False
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.closed = True
    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code))


class HttpTests(unittest.TestCase):
    def test_timeout_response_closure_and_transient_status_retry(self):
        responses = [Response(503), Response()]
        first, second = responses
        class Session:
            def get(inner, url, timeout):
                self.assertEqual(timeout, 5)
                return responses.pop(0)
        sleeps = []
        soup = fetch_html('https://example.org/course', session=Session(), timeout=5, sleep=sleeps.append)
        self.assertEqual(soup.h1.text, 'Course')
        self.assertEqual(sleeps, [1])
        self.assertTrue(first.closed and second.closed)

    def test_not_found_is_not_retried(self):
        class Session:
            def get(inner, url, timeout):
                return Response(404)
        with self.assertRaises(requests.HTTPError):
            fetch_html('https://example.org/course', session=Session(), sleep=lambda _: self.fail('retried'))
