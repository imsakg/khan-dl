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


from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BatchResult:
    url: str
    success: bool
    media_id: Optional[str] = None
    error: Optional[str] = None


class BatchRunner:
    def __init__(self, downloader, fail_fast=False, callback=None):
        self.downloader = downloader
        self.fail_fast = fail_fast
        self.callback = callback

    def run(self, urls):
        results = []
        for url in urls:
            try:
                info = self.downloader.download(url)
                result = BatchResult(url, True, media_id=info.get('id'))
            except Exception as error:
                result = BatchResult(url, False, error=str(error))
            results.append(result)
            if self.callback is not None:
                self.callback(result)
            if not result.success and self.fail_fast:
                break
        return results
