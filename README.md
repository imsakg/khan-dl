# khan-dl

Download public Khan Academy course videos, or queue individual media URLs.
This fork keeps the original course-selection interface and adds audio extraction,
subtitles, FFmpeg conversion, progress, retries and batch reports.

Original project: [rand-net/khan-dl](https://github.com/rand-net/khan-dl).
Local fork: [imsakg/khan-dl](https://github.com/imsakg/khan-dl). MIT licensed.

## Install this checkout

Use Python 3.8 or newer (the verification environment uses Python 3.11).
Install FFmpeg **and ffprobe** separately and put them on PATH for audio extraction,
video conversion, caption conversion and combining separate video/audio streams.

```sh
python -m pip install .
# Optional full-screen course picker:
python -m pip install '.[interactive]'
khan-dl --help
```

The changes in this checkout are not claimed to be available in a published PyPI
release. Install from this directory to get this version.

## Quick start

```sh
# Course discovery uses historical Khan Academy public-page markup.
khan-dl -c https://www.khanacademy.org/math/linear-algebra -o lessons

# Inspect metadata and available formats as newline-delimited JSON, no media files.
khan-dl --url 'https://www.youtube.com/watch?v=VIDEO_ID' --dry-run

# Download a public video, optionally cap its resolution.
khan-dl --url 'https://www.youtube.com/watch?v=VIDEO_ID' --max-height 720 -o videos

# Extract audio (FFmpeg required).
khan-dl --url 'https://www.youtube.com/watch?v=VIDEO_ID' -x --audio-format mp3 --audio-quality 192

# Download captions only, converting a fallback track to SRT if necessary.
khan-dl --url 'https://www.youtube.com/watch?v=VIDEO_ID' --skip-download --sub-langs en,tr --sub-format srt

# Batch, persist completed media IDs and checkpoint a JSON report after each item.
khan-dl --batch-file urls.txt --download-archive state/downloads.txt --report state/result.json -o lessons
```

Replace `VIDEO_ID` with a real authorized media ID. A manifest is UTF-8, one HTTP(S)
URL per line; blank lines and lines starting with `#` are ignored. Duplicates are
removed in their original order. Batches are serial and continue after failures
unless `--fail-fast` is supplied. Interactive selection is `khan-dl -i`; downloading
every catalog course is explicit `khan-dl --all` and may be very large.

## Behavior

- Video defaults to `bestvideo+bestaudio/best`; audio defaults to `bestaudio/best`.
- `--max-height` applies to the default video selector. It cannot be combined with
  an explicit `--format`; explicit audio selectors such as `worstaudio` are kept.
- Partial downloads resume by default. Existing downloads and converted outputs
  are protected; `--overwrite` explicitly replaces outputs and disables resume.
- Progress and summaries go to stderr. `--dry-run` emits metadata JSON to stdout;
  failed inspections follow the same continue/fail-fast policy as downloads.
- Exit codes: `0` success (including already-present/archived items), `1` item or
  discovery failures, `2` invalid input/configuration or report-path failure,
  `130` cancellation. Quiet mode suppresses normal progress, not errors/warnings.

See [formats and subtitles](docs/formats.md), [batches and recovery](docs/batches.md),
[development and tests](docs/development.md), and [timestamp provenance](docs/history-provenance.md).

## Limits and responsible use

The course and catalog selectors come from historical HTML. They can fail if Khan
Academy changes markup; direct public media URLs can be used separately. Extraction
is supplied by youtube-dl, so service-side changes can also break extraction. The
offline test suite exercises real local transfers and FFmpeg outputs, **not current
YouTube or Khan Academy availability**. Missing subtitle languages cannot be invented.
No DRM bypass, account login, cookies, paid-course access or parallel downloading
is provided. Download only material you have permission to keep and respect the
source service's terms and copyright requirements.
