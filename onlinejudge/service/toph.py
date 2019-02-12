# Python Version: 3.x
import posixpath
import string
import urllib.parse
from typing import *

import bs4
import requests
import re

import onlinejudge.dispatch
import onlinejudge.implementation.logging as log
import onlinejudge.implementation.utils as utils
import onlinejudge.type
from onlinejudge.type import SubmissionError


@utils.singleton
class TophService(onlinejudge.type.Service):
    def get_url(self) -> str:
        return 'https://toph.co/'

    def get_name(self) -> str:
        return 'toph'

    @classmethod
    def from_url(cls, s: str) -> Optional['TophService']:
        # example: https://toph.co/
        # example: http://toph.co/
        result = urllib.parse.urlparse(s)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'toph.co':
            return cls()
        return None

class TophProblem(onlinejudge.type.Problem):
    def __init__(self, slug: str, kind: Optional[str] = None):
        assert isinstance(slug, str)
        assert kind in (None, 'problem')
        self.kind = kind
        self.slug = slug

    def download_sample_cases(self, session: Optional[requests.Session] = None) -> List[onlinejudge.type.TestCase]:
        session = session or utils.new_default_session()
        resp = utils.request('GET', self.get_url(), session=session)
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        samples = utils.SampleZipper()
        for case in soup.find('table', class_="samples").find('tbody').find_all('tr'):
            log.debug('case: %s', str(case))
            assert len(list(case.children))
            input_pre, output_pre = list(map(lambda td: td.find('pre'), list(case.children)))
            assert input_pre.name == 'pre'
            assert output_pre.name == 'pre'
            assert re.search("^preSample.*Input$", input_pre.attrs['id'])
            assert re.search("^preSample.*Output$", output_pre.attrs['id'])
            s = input_pre.get_text()
            s = s.lstrip()
            samples.add(s, "Input")
            s = output_pre.get_text()
            s = s.lstrip()
            samples.add(s, "Output")
        return samples.get()

    def get_url(self) -> str:
        table = {}
        table['problem'] = 'https://toph.co/p/{}'
        return table[self.kind].format(self.slug)

    def get_service(self) -> TophService:
        return TophService()

    @classmethod
    def from_url(cls, s: str) -> Optional['TophProblem']:
        result = urllib.parse.urlparse(s)
        dirname, basename = posixpath.split(utils.normpath(result.path))
        if result.scheme in ('', 'http', 'https') \
                and result.netloc.count('.') == 1 \
                and result.netloc.endswith('toph.co') \
                and dirname == '/p' \
                and basename:
            kind = 'problem'
            slug = basename
            return cls(slug, kind)

        return None

onlinejudge.dispatch.services += [TophService]
onlinejudge.dispatch.problems += [TophProblem]
