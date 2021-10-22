"""Command line entry point."""
import argparse
from . import __version__
from .options import DownloadOptions


def build_parser():
    parser = argparse.ArgumentParser(description="Download Khan Academy courses")
    sources = parser.add_mutually_exclusive_group(required=True)
    sources.add_argument('-i', '--interactive', action='store_true')
    sources.add_argument('-c', '--course_url')
    sources.add_argument('-a', '--all', action='store_true')
    sources.add_argument('--url', help='Download one public media URL')
    sources.add_argument('--batch-file', help='UTF-8 file of media URLs')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('-o', '--output', default='.', help='Output directory')
    parser.add_argument('-x', '--extract-audio', action='store_true')
    parser.add_argument('--audio-format', default='mp3')
    parser.add_argument('--audio-quality', default='192')
    parser.add_argument('--convert-video', dest='video_format')
    parser.add_argument('--max-height', dest='height', type=int)
    parser.add_argument('-f', '--format', dest='format_selector', default='bestvideo+bestaudio/best')
    parser.add_argument('--sub-langs', default='', help='Comma-separated subtitle languages')
    parser.add_argument('--write-auto-subs', action='store_true')
    parser.add_argument('--skip-download', action='store_true', help='Download subtitles only')
    parser.add_argument('--sub-format', default='best')
    parser.add_argument('--retries', type=int, default=3)
    parser.add_argument('--timeout', type=float, default=30)
    parser.add_argument('--limit-rate', type=int)
    parser.add_argument('--no-continue', dest='continue_download', action='store_false')
    parser.add_argument('--overwrite', action='store_true')
    parser.add_argument('--write-info-json', action='store_true')
    parser.add_argument('--download-archive')
    parser.add_argument('--ffmpeg-location')
    parser.add_argument('-q', '--quiet', action='store_true')
    parser.add_argument('--fail-fast', action='store_true')
    parser.add_argument('--report', help='Atomic JSON batch result path')
    parser.add_argument('--dry-run', action='store_true')
    return parser


def options_from_args(args):
    return DownloadOptions(mode='audio' if args.extract_audio else 'video', output=args.output,
        audio_format=args.audio_format, audio_quality=args.audio_quality,
        video_format=args.video_format, height=args.height, format_selector=args.format_selector,
        subtitle_languages=tuple(part.strip() for part in args.sub_langs.split(',') if part.strip()),
        automatic_subtitles=args.write_auto_subs, subtitle_only=args.skip_download,
        subtitle_format=args.sub_format, retries=args.retries, timeout=args.timeout,
        rate_limit=args.limit_rate, continue_download=args.continue_download,
        overwrite=args.overwrite, write_metadata=args.write_info_json,
        archive=args.download_archive, ffmpeg_location=args.ffmpeg_location, quiet=args.quiet)


def main(argv=None):
    import sys
    from .batch import BatchRunner, read_manifest
    from .media import MediaDownloader
    from .reports import write_report
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        options = options_from_args(args)
        if args.url or args.batch_file:
            if args.batch_file:
                with open(args.batch_file, encoding='utf-8-sig') as stream:
                    urls = read_manifest(stream)
            else:
                from .urls import validate_url
                urls = [validate_url(args.url)]
            results = BatchRunner(MediaDownloader(options), fail_fast=args.fail_fast).run(urls)
        else:
            from .khan_downloader import Khan_DL
            from .interactive_prompt import course_selection_prompt, get_all_course_urls
            urls = ([course_selection_prompt()] if args.interactive else
                    get_all_course_urls() if args.all else [args.course_url])
            results = []
            for url in urls:
                course = Khan_DL('', url)
                course.get_course_html()
                course.generate_unit_slugs()
                course.generate_unit_urls()
                course.generate_course_slugs_video_ids()
                results.extend(course.download_videos())
        if args.report:
            write_report(args.report, results)
        for result in results:
            if not result.success:
                print('{}: {}'.format(result.url, result.error), file=sys.stderr)
        if not args.quiet:
            print('{} completed, {} failed'.format(sum(r.success for r in results),
                                                  sum(not r.success for r in results)), file=sys.stderr)
        return 1 if any(not r.success for r in results) else 0
    except (ValueError, OSError) as error:
        parser.error(str(error))
    except KeyboardInterrupt:
        return 130
