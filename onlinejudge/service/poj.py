# Python Version: 3.x
import urllib.parse
from typing import *

import bs4
import requests

import onlinejudge.dispatch
import onlinejudge.implementation.logging as log
import onlinejudge.implementation.utils as utils
import onlinejudge.type
from onlinejudge.type import LabeledString, TestCase


@utils.singleton
class POJService(onlinejudge.type.Service):
    def get_url(self) -> str:
        # no HTTPS support  (Wed Feb  6 14:35:37 JST 2019)
        return 'http://poj.org/'

    def get_name(self) -> str:
        return 'poj'

    @classmethod
    def from_url(cls, s: str) -> Optional['POJService']:
        # example: http://poj.org/
        result = urllib.parse.urlparse(s)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'poj.org':
            return cls()
        return None


class POJProblem(onlinejudge.type.Problem):
    def __init__(self, problem_id: int):
        self.problem_id = problem_id

    def download_sample_cases(self, session: Optional[requests.Session] = None) -> List[onlinejudge.type.TestCase]:
        session = session or utils.new_default_session()
        # get
        resp = utils.request('GET', self.get_url(), session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        in_pre, out_pre = soup.find_all('pre', class_='sio')
        in_p = in_pre.find_previous_sibling('p', class_='pst')
        out_p = out_pre.find_previous_sibling('p', class_='pst')
        assert in_p.text.strip() == 'Sample Input'
        assert out_p.text.strip() == 'Sample Output'
        return [TestCase(LabeledString(in_p.text.strip(), in_pre.text), LabeledString(out_p.text.strip(), out_pre.text))]

    def get_url(self) -> str:
        return 'http://poj.org/problem?id={}'.format(self.problem_id)

    def get_service(self) -> POJService:
        return POJService()

    @classmethod
    def from_url(cls, s: str) -> Optional['POJProblem']:
        # example: http://poj.org/problem?id=2104
        result = urllib.parse.urlparse(s)
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
