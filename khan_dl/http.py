"""Bounded course-page fetching with HTTP status checks and timeout handling."""
import time
import requests
from bs4 import BeautifulSoup
from .retry import retry_call
from .urls import validate_url


def fetch_html(url, session=None, timeout=30, retries=3, sleep=time.sleep):
    validate_url(url)
    if timeout <= 0:
        raise ValueError('timeout must be positive')
    client = session or requests
    def operation():
        with client.get(url, timeout=timeout) as response:
            if response.status_code == 429 or 500 <= response.status_code < 600:
                raise requests.ConnectionError('temporary HTTP {}'.format(response.status_code))
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
    return retry_call(operation, retries=retries, sleep=sleep,
                      exceptions=(requests.ConnectionError, requests.Timeout))
