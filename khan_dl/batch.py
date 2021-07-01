"""Serial download queues and UTF-8 line manifests."""
from .urls import validate_url


def read_manifest(stream):
    urls = []
    seen = set()
    for number, line in enumerate(stream, 1):
        url = line.strip()
        if not url or url.startswith('#'):
            continue
        try:
            validate_url(url)
        except ValueError as error:
            raise ValueError('manifest line {}: {}'.format(number, error)) from error
        if url not in seen:
            seen.add(url)
            urls.append(url)
    return urls
