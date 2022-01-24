# Development and verification

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install '.[interactive,dev]'
python -m unittest discover -s tests -v
python -m compileall -q khan_dl
git diff --check
python -m build
```

The declared minimum is Python 3.8; the local release checks use Python 3.11.
FFmpeg and ffprobe must be on PATH for integration tests, which otherwise skip
explicitly. No pytest dependency is needed. Tests create and clean their own
fixtures under the configured TMPDIR; the HTTP server binds only to loopback,
uses an OS-assigned port, and is shut down/joined during cleanup.

## Architecture

- `options.py`: immutable validated configuration shared across clients.
- `media.py`: lazy youtube-dl adapter, format selection, output protection and
  postprocessing; injectable backend/sleep for deterministic tests.
- `progress.py`: normalized byte events and throttled stderr rendering.
- `retry.py`, `http.py`: bounded retries and checked, timed course-page requests.
- `batch.py`, `reports.py`: ordered failure isolation and atomic per-item reports.
- `courses.py`, `khan_downloader.py`: pure parsing and compatibility course facade.
- `cli.py`: argument mapping, inspection/download modes and exit codes.

Package import and help do not import youtube-dl, requests or the optional
interactive UI. `Khan_DL` and `khan_dl.main` remain available; application code can
use `MediaDownloader(DownloadOptions(...))` and `BatchRunner` directly. The old
`topic_matcher.py` remains as a legacy compatibility module, but the active course
pipeline no longer guesses IDs with fuzzy string matching.

## What the tests establish

Unit tests cover configuration, URL/path safety, retry bounds, progress, ordered
manifests, failure isolation, CLI propagation and report atomicity/cancellation.
Integration tests generate a short synthetic MP4 with FFmpeg, serve it and a
WebVTT track on loopback HTTP, and use the actual youtube-dl/FFmpeg pipeline. They
compare downloaded video bytes, probe real MP3/MKV output streams, convert
caption-only SRT, check archive behavior and protect existing converted outputs.
No fabricated external API responses are presented as live-service evidence.

The tests do **not** establish current external Khan Academy/YouTube availability,
all-platform runtime support, every possible codec or extractor, interrupted
HTTP Range recovery on every server, or concurrent archive safety. Synthetic
HTML parser fixtures are deliberately small, not snapshots claimed to come from
the live site. Before changing course selectors, inspect authorized live evidence
and add an attributed fixture rather than silently weakening parsing errors.

See [history provenance](history-provenance.md) before interpreting commit dates.
