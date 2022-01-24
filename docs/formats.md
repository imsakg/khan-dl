# Formats, extraction and subtitles

## Video

The default selector `bestvideo+bestaudio/best` prefers separate high-quality
streams with a combined-stream fallback. FFmpeg is required to merge separate
streams. Use `--format best` to choose a combined format when one is offered, or
inspect `--dry-run` JSON and specify a format ID. Output names retain the actual
media extension, with extractor title and ID to reduce collisions.

`--max-height 720` becomes
`bestvideo[height<=720]+bestaudio/best[height<=720]`. It does not upscale media and
may fail if there is no format within the cap. To avoid silently changing an
explicit selection, combining `--max-height` and a custom `--format` is rejected.
Audio mode selects audio independently, so a video height cap has no effect there.

```sh
khan-dl --url URL --convert-video mkv --ffmpeg-location /path/to/ffmpeg
```

Supported conversion containers are mp4, mkv, webm, avi, flv and ogg. Conversion
uses youtube-dl's FFmpeg postprocessor; output codec compatibility depends on the
installed FFmpeg build. This is conversion, not a promise of lossless remuxing.

## Audio

```sh
khan-dl --url URL -x --audio-format flac
khan-dl --url URL -x --audio-format mp3 --audio-quality 192
khan-dl --url URL -x --format worstaudio --audio-format opus
```

Codecs: mp3, m4a, aac, flac, wav, opus, vorbis, best. Quality is an integer: 0–9
is an FFmpeg quality setting where supported; larger values are kbps. Do not add
`k` to the number. Quality behavior varies by codec and copying a compatible
stream may ignore the requested bitrate. FLAC cannot restore detail lost in a
lossy source. Audio extraction and video conversion are mutually exclusive.

## Subtitles

```sh
khan-dl --url URL --sub-langs en,tr --sub-format srt
khan-dl --url URL --skip-download --sub-langs en --write-auto-subs
```

Human captions are requested with `--sub-langs`; `--write-auto-subs` opts into
extractor-provided automatic captions. `--skip-download` requests captions without
media (English is youtube-dl's default when no language list is provided).
Subtitle formats are best, srt, vtt and ttml. A named format first requests that
format, then falls back to an offered track and converts using FFmpeg. Caption-only
conversion is explicitly handled because youtube-dl skips ordinary postprocessing
when media download is disabled. No captions are manufactured when a requested
language is unavailable; inspect metadata/warnings before assuming it exists.

Existing converted captions are preserved unless `--overwrite` is explicit.
A progress event named `finished` means the transfer finished; the batch item is
successful only after any conversion/postprocessing also completes.
