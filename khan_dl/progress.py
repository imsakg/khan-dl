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
