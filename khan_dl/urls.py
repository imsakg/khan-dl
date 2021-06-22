"""Validate explicit public-media URL syntax before invoking an extractor."""
from urllib.parse import urlsplit


def validate_url(url):
    if not isinstance(url, str) or any(c.isspace() or ord(c) < 32 for c in url):
        raise ValueError('URL must be a nonempty HTTP(S) URL without whitespace')
    parts = urlsplit(url)
    if parts.scheme not in ('http', 'https') or not parts.hostname:
        raise ValueError('only HTTP(S) URLs with a host are supported')
    if parts.username is not None or parts.password is not None:
        raise ValueError('credentials in URLs are not supported')
    if parts.port is not None and parts.port == 0:
        raise ValueError('port must be between 1 and 65535')
    return url
