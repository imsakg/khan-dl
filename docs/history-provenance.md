# Local development series and timestamp provenance

This fork adds a tested download pipeline: video and audio selection, subtitles,
FFmpeg conversion, progress, resumable archives, retry and serial batch handling.
The original course-discovery interface remains available.

## Dates are assigned, not evidence of contemporaneous work

The changes in this local series were developed in October 2026. At the repository
owner's explicit request, their author and committer timestamps are assigned to
randomized weekday evenings between February 2021 and January 2022. Those dates
must not be represented as when this development actually occurred. Original
commits and attribution are preserved, including their earlier dates; assigned
child dates can precede original parent dates.

The starting checkout is `15d6339`, with **40 reachable commits**, rather than the
estimated 11. The planned series adds 40 substantive commits to reach 80 total.
No push is part of this work. Each change has a descriptive message and real code,
tests, documentation or packaging content; no empty padding commits are used.

## Scope and verification

The adapter delegates public-media extraction and download to youtube-dl. FFmpeg
is needed for audio extraction, remuxing and format conversion. Tests use injected
backends plus locally served media; they do not prove that historical Khan Academy
HTML selectors or current YouTube extraction work against the live services.
Download only material you are authorized to keep, respect service terms, and do
not use this tool to circumvent access controls.
