# Batches, progress and recovery

Create a UTF-8 manifest (`urls.txt`):

```text
# Authorized public media
https://www.youtube.com/watch?v=FIRST_ID
https://www.youtube.com/watch?v=SECOND_ID
```

```sh
khan-dl --batch-file urls.txt -o lessons --retries 3 --timeout 30 \
  --limit-rate 1048576 --download-archive state/videos.txt --report state/report.json
```

`--limit-rate` is bytes per second. `--retries` is additional whole-operation
attempts, so zero means a single attempt. Extraction/download failures use capped
exponential waits of 1, 2, 4 … seconds (maximum 30); requests for course pages retry
connection/timeouts, HTTP 429 and 5xx, but not ordinary 4xx errors. Media HTTP
retry policy is delegated through youtube-dl DownloadError handling; permanent
media errors may therefore consume the bounded retry budget. Fragment retries
have their own backend budget; total network requests can exceed the attempt count.
Configured HTTP limits also apply to interactive/catalog discovery.

Each item gets a fresh backend context. Batch errors are isolated and order is
preserved; `--fail-fast` stops at the first failure. `--all` also records a failed
course-discovery attempt and continues to later courses unless fail-fast is set.
Progress events expose downloaded bytes, known/estimated totals, percent, speed,
ETA and transfer state. Unknown totals remain unknown, not fabricated percentages.
Normal terminal updates are throttled; final transfer events are not suppressed.

## Resume and existing files

Partial files resume by default. `--no-continue` disables partial resumption but
does not by itself authorize replacing existing outputs. `--overwrite` disables
resumption and permits replacing downloaded/converted outputs. Prefer separate
output directories and archives for different audio/video/quality profiles.

The youtube-dl archive records completed **media IDs**, not format-specific jobs.
Changing quality or converting to another format does not invalidate archive
entries. Deleting a file does not remove its archive entry. Caption-only runs do
not add media archive entries, though an existing media entry can cause the backend
to skip processing; use a separate/no archive for caption-only work. Archive
parent directories are created before downloading, but it is not a transactional
multi-process database: do not share an archive across concurrent processes.

## JSON reports and cancellation

`--report` writes UTF-8 JSON with `total`, `succeeded`, `failed` and ordered
`results` containing URL, success, media ID and error. Counts describe attempted
items (and failed course discoveries), not all queued URLs or newly created files.
Already-present/archived outputs count as successful attempts, not fresh transfers.
Reports checkpoint after every item using a temporary file and atomic replacement.
They preserve completed work on Ctrl-C; the in-flight item is not misreported as
complete. Ctrl-C exits 130. Report I/O failures stop the run rather than silently
losing completion evidence. Dry-run reports are allowed only when explicitly
requested and describe inspection attempts, not media downloads.

A report is an audit summary, **not** the resume authority. Rerun the same manifest
with the same archive/output directory to resume. There is no parallel scheduling,
automatic failed-only manifest rewrite, or cross-process locking.
