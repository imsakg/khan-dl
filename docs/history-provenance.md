# Local development series and timestamp provenance

This fork adds a tested download pipeline: video and audio selection, subtitles,
FFmpeg conversion, progress, resumable archives, retry and serial batch handling.
The original course-discovery interface remains available.

## Dates are assigned, not evidence of contemporaneous work

The changes in this local series were developed in October 2026. At the repository
owner's explicit request, their author and committer timestamps are assigned to
randomized weekday evenings between February 2021 and January 2022. Those dates
must not be represented as when this development actually occurred. File-level
attribution and the baseline tree are retained; assigned child dates can precede
baseline parent dates. See the concurrent-history exception below before making
claims about unchanged original commit IDs.

The starting checkout was `15d6339`, with **40 reachable commits**, rather than the
estimated 11. This series adds 40 substantive commits to reach 80 total. Each
change has a descriptive message and real code, tests, documentation or packaging
content; no empty padding commits are used.

## Concurrent-history and remote-state exception

During execution, a separate operation rewrote the original 40-commit ancestry;
the resulting baseline is `9cd43b9ee32d1d19d42202affec1edc9797cd457`.
`git diff 15d6339 9cd43b9 --` was empty: the baseline files are unchanged, but the
original commit hashes/timestamp metadata are not unchanged on main. The original
history remains reachable through the existing local `refs/original/refs/heads/main`
backup at the time of verification. This series does not undo that concurrent
rewrite and dates only its own 40 commits using `git commit --date` followed by
`git rebase --committer-date-is-author-date`.

The implementing agent issued **no push** and did not authorize a remote rollback.
Nevertheless, the repository reflog records an `update by push` at
`2026-10-15T15:59:27+03:00`, pointing `origin/main` to
`603d570faf36eb5e72a935b6300da563261637b5` (the second new commit before the final
local dating rebase). A read-only `git ls-remote origin refs/heads/main` confirmed
that SHA. Consequently, this session cannot certify the owner's no-push invariant
for the checkout as a whole. The completed series is kept local; no remote write
or attempt to reverse the external push is part of this implementation.

## Scope and verification

The adapter delegates public-media extraction and download to youtube-dl. FFmpeg
is needed for audio extraction, remuxing and format conversion. Tests use injected
backends plus locally served media; they do not prove that historical Khan Academy
HTML selectors or current YouTube extraction work against the live services.
Download only material you are authorized to keep, respect service terms, and do
not use this tool to circumvent access controls.
