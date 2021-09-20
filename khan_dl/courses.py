"""Pure parsing helpers for the historical public Khan Academy markup."""
import re
from urllib.parse import urljoin, urlsplit
from .urls import validate_url


def extract_video_ids(html):
    return list(dict.fromkeys(re.findall(r'"youtubeId"\s*:\s*"([A-Za-z0-9_-]{11})"', str(html))))


def course_title(soup):
    node = soup.find(attrs={'data-test-id': 'unit-block-title'}) or soup.find('title')
    return node.get_text(' ', strip=True) if node else 'Khan Academy course'


def parse_units(soup, base_url):
    units, seen = [], set()
    for node in soup.find_all(attrs={'data-test-id': 'unit-header'}):
        if not node.get('href'):
            continue
        url = validate_url(urljoin(base_url, node['href']))
        if urlsplit(url).hostname not in ('www.khanacademy.org', 'khanacademy.org'):
            raise ValueError('unit link points outside Khan Academy')
        if url not in seen:
            seen.add(url)
            units.append((node.get_text(' ', strip=True) or 'Unit', url))
    if not units:
        raise ValueError('No course unit links found; Khan Academy markup may have changed')
    return units
