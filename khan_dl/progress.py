"""Normalize youtube-dl progress hooks without parsing terminal strings."""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ProgressEvent:
    status: str
    filename: str
    downloaded: int
    total: Optional[int]
    percent: Optional[float]
    speed: Optional[float]
    eta: Optional[float]


class ProgressTracker:
    def __init__(self, callback=None):
        self.callback = callback
        self.latest = None

    def __call__(self, data):
        downloaded = max(0, data.get('downloaded_bytes') or 0)
        total = data.get('total_bytes') or data.get('total_bytes_estimate')
        total = total if total and total > 0 else None
        percent = min(100.0, 100.0 * downloaded / total) if total else None
        self.latest = ProgressEvent(data.get('status', 'unknown'), data.get('filename', ''),
                                    downloaded, total, percent, data.get('speed'), data.get('eta'))
        if self.callback is not None:
            self.callback(self.latest)


class TerminalProgress:
    """Throttled line output; finished means transfer done, not conversion done."""
    def __init__(self, stream=None, interval=0.5, clock=None):
        import sys
        import time
        self.stream = stream if stream is not None else sys.stderr
        self.interval = interval
        self.clock = clock or time.monotonic
        self.last_time = None

    def __call__(self, event):
        now = self.clock()
        if event.status == 'downloading' and self.last_time is not None and now - self.last_time < self.interval:
            return
        self.last_time = now
        size = '{:.1f}%'.format(event.percent) if event.percent is not None else '{} bytes'.format(event.downloaded)
        filename = ''.join(c for c in event.filename if c.isprintable())
        print('{} {} {}'.format(event.status, size, filename).rstrip(), file=self.stream, flush=True)
