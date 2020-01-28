# Python Version: 3.x
# -*- coding: utf-8 -*-
"""
the module for Sphere Online Judge (https://www.spoj.com/)

"""

import re
import urllib.parse
from typing import *

import bs4
import requests

import onlinejudge._implementation.logging as log
import onlinejudge._implementation.testcase_zipper
import onlinejudge._implementation.utils as utils
import onlinejudge.type
from onlinejudge.type import TestCase


class SPOJService(onlinejudge.type.Service):
    def get_url(self) -> str:
        return 'https://www.spoj.com/'

    def get_name(self) -> str:
        return 'Sphere Online Judge'

    @classmethod
    def from_url(cls, url: str) -> Optional['SPOJService']:
        # example: https://www.spoj.com/
        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc in ('www.spoj.com',):
            return cls()
        return None


class SPOJProblem(onlinejudge.type.Problem):
    """
    :ivar problem_id: :py:class:`str` like `TEST` or `PRIME1`
    """
    def __init__(self, *, problem_id):
        self.problem_id = problem_id

    def download_sample_cases(self, *, session: Optional[requests.Session] = None) -> List[TestCase]:
        """
        :raises SampleParseError:
        """
        session = session or utils.get_default_session()

        url = 'https://www.spoj.com/problems/{}'.format(self.problem_id)
        resp = utils.request('GET', url, session=session)
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        samples = onlinejudge._implementation.testcase_zipper.SampleZipper()
        for pre, h3 in self._find_sample_tags(soup):
            s = utils.textfile(utils.dos2unix(utils.parse_content(pre).lstrip()))
            name = h3.string
            samples.add(s.encode(), name)
        return samples.get()

    def _find_sample_tags(cls, soup: bs4.BeautifulSoup) -> Iterator[Tuple[bs4.Tag, bs4.Tag]]:
        expected_strings = ('Sample Input:', 'Sample Output:')

        def get_header(tag, expected_tag_name):
            if tag and tag.name == expected_tag_name and tag.string and any(s in tag.string for s in expected_strings):
                return tag
            return None

        for pre in soup.find(id='problem-body').find_all('pre'):
            log.debug('pre tag: %s', str(pre))
            tag = pre.find_previous_sibling().find_previous_sibling()
            h3 = get_header(tag=tag, expected_tag_name='b')

            if h3:
                yield (pre, h3)
                continue
        samples = []  # type: List[TestCase]

        return samples

    def get_url(self) -> str:
        return 'https://www.spoj.com/problems/{}'.format(self.problem_id)

    @classmethod
    def from_url(cls, url: str) -> Optional['SPOJProblem']:
        # example: https://www.spoj.com/problems/PRIME1/
        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'www.spoj.com':
            m = re.match(r'/(?:problems)/([0-9A-Z_a-z-]+)/?', result.path)
            if m:
                problem_id = m.group(1)
                return cls(problem_id=problem_id)
        return None

    def get_service(self) -> SPOJService:
        return SPOJService()


onlinejudge.dispatch.services += [SPOJService]
onlinejudge.dispatch.problems += [SPOJProblem]
