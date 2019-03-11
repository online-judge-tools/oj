# Python Version: 3.x
"""
the module for PKU JudgeOnline (http://poj.org/)
"""

import urllib.parse
from typing import *

import bs4
import requests

import onlinejudge._implementation.logging as log
import onlinejudge._implementation.utils as utils
import onlinejudge.dispatch
import onlinejudge.type
from onlinejudge.type import TestCase


class POJService(onlinejudge.type.Service):
    def get_url(self) -> str:
        # no HTTPS support  (Wed Feb  6 14:35:37 JST 2019)
        return 'http://poj.org/'

    def get_name(self) -> str:
        return 'PKU JudgeOnline'

    @classmethod
    def from_url(cls, url: str) -> Optional['POJService']:
        # example: http://poj.org/
        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'poj.org':
            return cls()
        return None


class POJProblem(onlinejudge.type.Problem):
    def __init__(self, problem_id: int):
        self.problem_id = problem_id

    def download_sample_cases(self, session: Optional[requests.Session] = None) -> List[TestCase]:
        session = session or utils.get_default_session()
        # get
        resp = utils.request('GET', self.get_url(), session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        in_pre, out_pre = soup.find_all('pre', class_='sio')
        in_p = in_pre.find_previous_sibling('p', class_='pst')
        out_p = out_pre.find_previous_sibling('p', class_='pst')
        log.debug('pre  (in): %s', in_pre.contents)
        log.debug('pre (out): %s', out_pre.contents)
        assert in_p.text.strip() == 'Sample Input'
        assert out_p.text.strip() == 'Sample Output'
        assert len(in_pre.contents) == len(out_pre.contents)
        samples = []  # type: List[TestCase]
        if len(in_pre.contents) == 1:
            assert isinstance(in_pre.contents[0], bs4.NavigableString)
            assert isinstance(out_pre.contents[0], bs4.NavigableString)
            samples += [TestCase(
                'sample',
                in_p.text.strip(),
                in_pre.text.encode() + b'\r\n',
                out_p.text.strip(),
                out_pre.text.encode() + b'\r\n',
            )]
        else:
            assert len(in_pre.contents) % 2 == 0
            for i in range(len(in_pre.contents) // 2):
                in_name = in_pre.contents[2 * i]
                in_data = in_pre.contents[2 * i + 1]
                out_name = out_pre.contents[2 * i]
                out_data = out_pre.contents[2 * i + 1]
                assert in_name.name == 'b'
                assert isinstance(in_data, bs4.NavigableString)
                assert out_name.name == 'b'
                assert isinstance(out_data, bs4.NavigableString)
                samples += [TestCase(
                    'sample-{}'.format(i + 1),
                    in_name.text.strip(),
                    str(in_data).strip().encode() + b'\r\n',
                    out_name.text.strip(),
                    str(out_data).strip().encode() + b'\r\n',
                )]
        return samples

    def get_url(self) -> str:
        return 'http://poj.org/problem?id={}'.format(self.problem_id)

    def get_service(self) -> POJService:
        return POJService()

    @classmethod
    def from_url(cls, url: str) -> Optional['POJProblem']:
        # example: http://poj.org/problem?id=2104
        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'poj.org' \
                and utils.normpath(result.path) == '/problem':
            query = urllib.parse.parse_qs(result.query)
            if 'id' in query and len(query['id']) == 1:
                try:
                    n = int(query['id'][0])
                    return cls(n)
                except ValueError:
                    pass
        return None


onlinejudge.dispatch.services += [POJService]
onlinejudge.dispatch.problems += [POJProblem]
