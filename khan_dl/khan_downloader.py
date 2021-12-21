"""Compatibility facade for course discovery and the shared media pipeline."""
from dataclasses import replace
from pathlib import Path
from urllib.parse import urlsplit
from .batch import BatchRunner
from .courses import course_title, extract_video_ids, parse_units
from .http import fetch_html
from .media import MediaDownloader
from .options import DownloadOptions
from .paths import safe_component
from .urls import validate_url


class Khan_DL:
    def __init__(self, output_rel_path, course_root_url, options=None,
                 page_fetcher=None, progress=None):
        validate_url(course_root_url)
        if urlsplit(course_root_url).hostname not in ('www.khanacademy.org', 'khanacademy.org'):
            raise ValueError('course URL must belong to Khan Academy')
        self.course_root_url = course_root_url
        self.output_rel_path = str(Path(output_rel_path or '.').expanduser().resolve())
        self.options = replace(options or DownloadOptions(), output=self.output_rel_path)
        self.page_fetcher = page_fetcher or fetch_html
        self.progress = progress
        self._units = None
        self.download_jobs = []

    def _fetch(self, url):
        return self.page_fetcher(url, timeout=self.options.timeout, retries=self.options.retries)

    def get_course_html(self):
        self.course_root_page_html = self._fetch(self.course_root_url)
        self._units = None
        return self.course_root_page_html

    def _parse_units(self):
        if self._units is None:
            self._units = parse_units(self.course_root_page_html, self.course_root_url)
        return self._units

    def generate_unit_slugs(self):
        title = safe_component(course_title(self.course_root_page_html))
        self.unit_headers = [name for name, url in self._parse_units()]
        self.unit_slugs = [str(Path(title) / ('{:02d}_'.format(index) + safe_component(name)))
                           for index, name in enumerate(self.unit_headers, 1)]
        return self.unit_slugs

    def generate_unit_urls(self):
        self.unit_urls = [url for name, url in self._parse_units()]
        return self.unit_urls

    def generate_course_slugs_video_ids(self):
        if len(self.unit_urls) != len(self.unit_slugs):
            raise ValueError('unit URL and output directory counts differ')
        self.youtube_id_list, self.full_course_slugs, self.download_jobs = [], [], []
        seen = set()
        for unit_url, slug in zip(self.unit_urls, self.unit_slugs):
            ids = extract_video_ids(self._fetch(unit_url))
            for video_id in ids:
                if video_id in seen:
                    continue
                seen.add(video_id)
                directory = str(Path(self.output_rel_path) / slug)
                self.youtube_id_list.append(video_id)
                self.full_course_slugs.append(directory)
                self.download_jobs.append(('https://www.youtube.com/watch?v=' + video_id, directory))
        if not self.download_jobs:
            raise ValueError('No video IDs found; Khan Academy markup may have changed')
        return self.download_jobs

    def download_videos(self, downloader=None, fail_fast=False, callback=None):
        media = downloader or MediaDownloader(self.options, progress=self.progress)
        directories = dict(self.download_jobs)
        class CourseMedia:
            def download(self, url):
                return media.download(url, directory=directories[url])
        return BatchRunner(CourseMedia(), fail_fast=fail_fast, callback=callback).run(directories)
