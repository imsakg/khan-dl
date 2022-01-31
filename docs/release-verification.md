# Version 1.1.0 local verification

Verified in October 2026 on macOS with Python 3.11.7, youtube-dl 2021.12.17 and
system FFmpeg/ffprobe. Historical commit timestamps are assigned metadata, not
execution dates; see [history provenance and the remote-state exception](history-provenance.md).

## Executed checks

- `python -m unittest discover -s tests -v`: **71 tests passed**, no skips in the
  verification environment. Local media integration exercised actual downloads,
  MP3 extraction, MKV conversion, SRT subtitles, existing-output preservation,
  explicit overwrite, download archives and metadata sidecars.
- `python -m compileall -q khan_dl`: passed.
- `git diff --check`: passed.
- `python -m build`: built both `khan_dl-1.1.0.tar.gz` and
  `khan_dl-1.1.0-py3-none-any.whl` in the external scratch artifact directory.
- Installed the wheel into a fresh isolated environment outside the source tree.
  `khan-dl --version` returned `1.1.0`; `--help` and `uv pip check` passed.
- Executed the **installed console command** against generated loopback HTTP media:
  MP3 output was probed as codec `mp3`; its atomic report contained total 1,
  succeeded 1, failed 0. Installed-CLI dry-run JSON reported the real source `mp4`.
- The temporary diagnostic review worktree was removed. Integration HTTP servers
  are shut down/closed and their threads joined by test cleanup.

## Review fixes

A separate diagnostic pass identified unsafe converted-output replacement,
ineffective explicit overwrite under resume, ignored format selectors, unisolated
dry-run/course failures, catalog HTTP limits and nested archive-path failures.
These were reproduced with regression tests and corrected before packaging.
Nonfinite timeouts, invalid audio quality and contradictory settings now fail
before network work. Atomic report failures preserve the previous complete file.

## Limits and warnings

No external Khan Academy or YouTube download was claimed or verified. Other
Python versions, platforms, extractors and codec combinations require their own
runtime checks. Expected generic-extractor warnings occur for the synthetic local
HTML fixture. Modern setuptools emits a nonfatal warning that license classifiers
are deprecated; the wheel and source distribution still build and install.

The intended local history is 40 baseline commits plus 40 nonempty new commits,
with new author and committer dates on randomized weekday evenings from
2021-02-01 through 2022-01-31 (+03:00). The repository's full ancestry begins in
January 2021. Final count/date/signature checks are run after the local rebase;
the concurrent external push documented in provenance is **not** undone.
