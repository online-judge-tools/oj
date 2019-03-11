# Python Version: 3.x
"""
the module for Kattis (http://open.kattis.org/)
"""

import io
import re
import urllib.parse
import zipfile
from typing import *

import bs4
import requests

import onlinejudge._implementation.logging as log
import onlinejudge._implementation.testcase_zipper
import onlinejudge._implementation.utils as utils
import onlinejudge.dispatch
import onlinejudge.type
from onlinejudge.type import TestCase


class KattisService(onlinejudge.type.Service):
    def get_url(self) -> str:
        """
        :note: sometimes this URL is not correct, i.e. something like https://hanoi18.kattis.com/ exists
        """

        return 'http://open.kattis.org/'

    def get_name(self) -> str:
        return 'Kattis'

    @classmethod
    def from_url(cls, url: str) -> Optional['KattisService']:
        # example: https://open.kattis.com/
        # example: https://hanoi18.kattis.com/
        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc.endswith('.kattis.com'):
            # NOTE: ignore the subdomain
            return cls()
        return None


class KattisProblem(onlinejudge.type.Problem):
    def __init__(self, problem_id: str, contest_id: Optional[str] = None, domain: str = 'open.kattis.com'):
        self.domain = domain
        self.contest_id = contest_id
        self.problem_id = problem_id

    def download_sample_cases(self, session: Optional[requests.Session] = None) -> List[onlinejudge.type.TestCase]:
        session = session or utils.get_default_session()
        # get
        url = self.get_url(contests=False) + '/file/statement/samples.zip'
        resp = utils.request('GET', url, session=session, raise_for_status=False)
        if resp.status_code == 404:
            log.warning('samples.zip not found')
            log.info('this 404 happens in both cases: 1. no sample cases as intended; 2. just an error')
            return []
        resp.raise_for_status()
        # parse
        return onlinejudge._implementation.testcase_zipper.extract_from_zip(resp.content, '%s.%e', out='ans')

    def get_url(self, contests: bool = True) -> str:
        if contests and self.contest_id is not None:
            # the URL without "/contests/{}" also works
            return 'https://{}/contests/{}/problems/{}'.format(self.domain, self.contest_id, self.problem_id)
        else:
            return 'https://{}/problems/{}'.format(self.domain, self.problem_id)

    def get_service(self) -> KattisService:
        # NOTE: ignore the subdomain
        return KattisService()

    @classmethod
    def from_url(cls, url: str) -> Optional['KattisProblem']:
        # example: https://open.kattis.com/problems/hello
        # example: https://open.kattis.com/contests/asiasg15prelwarmup/problems/8queens
        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc.endswith('.kattis.com'):
            m = re.match(r'(?:/contests/([0-9A-Z_a-z-]+))?/problems/([0-9A-Z_a-z-]+)/?', result.path)
            if m:
                contest_id = m.group(1) or None
                problem_id = m.group(2)
                return cls(problem_id, contest_id=contest_id, domain=result.netloc)
        return None


onlinejudge.dispatch.services += [KattisService]
onlinejudge.dispatch.problems += [KattisProblem]
