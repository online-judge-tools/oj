# Python Version: 3.x
# -*- coding: utf-8 -*-
"""
the module for Aizu Online Judge (http://judge.u-aizu.ac.jp/onlinejudge/)
"""

import collections
import io
import itertools
import json
import posixpath
import re
import urllib.parse
import zipfile
from typing import *

import requests

import onlinejudge.dispatch
import onlinejudge.implementation.logging as log
import onlinejudge.implementation.utils as utils
import onlinejudge.type
from onlinejudge.type import LabeledString, TestCase


@utils.singleton
class AOJService(onlinejudge.type.Service):
    def get_url(self) -> str:
        return 'http://judge.u-aizu.ac.jp/onlinejudge/'

    def get_name(self) -> str:
        return 'aoj'

    @classmethod
    def from_url(cls, url: str) -> Optional['AOJService']:
        # example: http://judge.u-aizu.ac.jp/onlinejudge/
        # example: https://onlinejudge.u-aizu.ac.jp/home
        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc in ('judge.u-aizu.ac.jp', 'onlinejudge.u-aizu.ac.jp'):
            return cls()
        return None


class AOJProblem(onlinejudge.type.Problem):
    def __init__(self, problem_id):
        self.problem_id = problem_id

    def download_sample_cases(self, session: Optional[requests.Session] = None) -> List[TestCase]:
        session = session or utils.new_default_session()
        # get samples via the official API
        # reference: http://developers.u-aizu.ac.jp/api?key=judgedat%2Ftestcases%2Fsamples%2F%7BproblemId%7D_GET
        url = 'https://judgedat.u-aizu.ac.jp/testcases/samples/{}'.format(self.problem_id)
        resp = utils.request('GET', url, session=session)
        samples = []  # type: List[TestCase]
        for sample in json.loads(resp.content.decode(resp.encoding)):
            samples += [TestCase(
                LabeledString(str(sample['serial']), sample['in']),
                LabeledString(str(sample['serial']), sample['out']),
            )]
        return samples

    def download_system_cases(self, session: Optional[requests.Session] = None) -> List[TestCase]:
        session = session or utils.new_default_session()

        # get header
        # reference: http://developers.u-aizu.ac.jp/api?key=judgedat%2Ftestcases%2F%7BproblemId%7D%2Fheader_GET
        url = 'https://judgedat.u-aizu.ac.jp/testcases/{}/header'.format(self.problem_id)
        resp = utils.request('GET', url, session=session)
        header = json.loads(resp.content.decode(resp.encoding))

        # get testcases via the official API
        testcases = []  # type: List[TestCase]
        for header in header['headers']:
            # reference: http://developers.u-aizu.ac.jp/api?key=judgedat%2Ftestcases%2F%7BproblemId%7D%2F%7Bserial%7D_GET
            url = 'https://judgedat.u-aizu.ac.jp/testcases/{}/{}'.format(self.problem_id, header['serial'])
            resp = utils.request('GET', url, session=session)
            testcase = json.loads(resp.content.decode(resp.encoding))
            skipped = False
            for type in ('in', 'out'):
                if testcase[type].endswith('..... (terminated because of the limitation)\n'):
                    log.error('AOJ API says: terminated because of the limitation')
                    skipped = True
            if skipped:
                log.warning("skipped due to the limitation of AOJ API")
                continue
            testcases += [TestCase(
                LabeledString(header['name'], testcase['in']),
                LabeledString(header['name'], testcase['out']),
            )]
        return testcases

    def get_url(self) -> str:
        return 'http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id={}'.format(self.problem_id)

    @classmethod
    def from_url(cls, url: str) -> Optional['AOJProblem']:
        result = urllib.parse.urlparse(url)

        # example: http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=1169
        # example: http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=DSL_1_A&lang=jp
        querystring = urllib.parse.parse_qs(result.query)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'judge.u-aizu.ac.jp' \
                and utils.normpath(result.path) == '/onlinejudge/description.jsp' \
                and querystring.get('id') \
                and len(querystring['id']) == 1:
            n, = querystring['id']
            return cls(n)

        # example: https://onlinejudge.u-aizu.ac.jp/challenges/sources/JAG/Prelim/2881
        # example: https://onlinejudge.u-aizu.ac.jp/courses/library/4/CGL/3/CGL_3_B
        m = re.match(r'^/(challenges|courses)/(sources|library/\d+|lesson/\d+)/(\w+)/(\w+)/(\w+)$', utils.normpath(result.path))
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'onlinejudge.u-aizu.ac.jp' \
                and m:
            n = m.group(5)
            return cls(n)

        # example: https://onlinejudge.u-aizu.ac.jp/services/room.html#RitsCamp18Day3/problems/B
        # NOTE: I don't know how to retrieve the problem id

        return None

    def get_service(self) -> AOJService:
        return AOJService()


onlinejudge.dispatch.services += [AOJService]
onlinejudge.dispatch.problems += [AOJProblem]
