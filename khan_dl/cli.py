"""Command line entry point."""
import argparse


def build_parser():
    parser = argparse.ArgumentParser(description="Download Khan Academy courses")
    sources = parser.add_mutually_exclusive_group(required=True)
    sources.add_argument('-i', '--interactive', action='store_true')
    sources.add_argument('-c', '--course_url')
    sources.add_argument('-a', '--all', action='store_true')
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    from .khan_downloader import Khan_DL
    from .interactive_prompt import course_selection_prompt, get_all_course_urls
    urls = ([course_selection_prompt()] if args.interactive else
            get_all_course_urls() if args.all else [args.course_url])
    for url in urls:
        course = Khan_DL('', url)
        course.get_course_html()
        course.generate_unit_slugs()
        course.generate_unit_urls()
        course.generate_course_slugs_video_ids()
        course.download_videos()
    return 0
