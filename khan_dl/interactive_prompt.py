"""Optional interactive catalog selection; HTTP work stays in the fetch layer."""
from urllib.parse import urljoin, urlsplit
from .http import fetch_html


course_domains = {'MATH': '/math', 'SCIENCE': '/science', 'ARTS & HUMANITIES': '/humanities',
                  'COMPUTING': '/computing', 'ECONOMICS': '/economics-finance-domain',
                  'TEST PREP': '/test-prep'}


def get_course_urls(course_domain):
    url = urljoin('https://www.khanacademy.org/', course_domain)
    if urlsplit(url).hostname != 'www.khanacademy.org':
        raise ValueError('catalog URL must belong to Khan Academy')
    soup = fetch_html(url)
    courses, seen = {}, set()
    for node in soup.find_all('a', class_='_1q2jm21'):
        href = node.get('href')
        if not href:
            continue
        course_url = urljoin(url, href)
        if urlsplit(course_url).hostname != 'www.khanacademy.org':
            continue
        if course_url not in seen:
            seen.add(course_url)
            title = node.get_text(' ', strip=True) or course_url
            # Do not silently discard two distinct courses with the same display title.
            if title in courses:
                title += ' (' + course_url + ')'
            courses[title] = course_url
    if not courses:
        raise ValueError('No catalog courses found; Khan Academy markup may have changed')
    return courses


def course_selection_prompt():
    from prompt_toolkit.shortcuts import radiolist_dialog
    domain = radiolist_dialog(title='Khan Academy', text='Select a domain',
                              values=[(path, name) for name, path in course_domains.items()]).run()
    if domain is None:
        raise KeyboardInterrupt()
    courses = get_course_urls(domain)
    course = radiolist_dialog(title='Khan Academy', text='Select a course',
                              values=[(url, name) for name, url in courses.items()]).run()
    if course is None:
        raise KeyboardInterrupt()
    return course


def get_all_course_urls():
    return list(dict.fromkeys(url for domain in course_domains.values()
                             for url in get_course_urls(domain).values()))
