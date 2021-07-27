"""Atomic machine-readable batch reports, including completed work after failure."""
from dataclasses import asdict
import json
import os
from pathlib import Path
import tempfile


def write_report(path, results):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {'total': len(results),
               'succeeded': sum(result.success for result in results),
               'failed': sum(not result.success for result in results),
               'results': [asdict(result) for result in results]}
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.tmp',
                                         dir=str(path.parent), delete=False) as stream:
            temporary = stream.name
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write(chr(10))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and os.path.exists(temporary):
            os.unlink(temporary)
