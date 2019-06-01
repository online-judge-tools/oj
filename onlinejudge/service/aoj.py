# Python Version: 3.x
# -*- coding: utf-8 -*-
"""
the module for Aizu Online Judge (http://judge.u-aizu.ac.jp/onlinejudge/)

:note: There is the offcial API http://developers.u-aizu.ac.jp/index
"""

import collections
import io
import itertools
import json
import posixpath
import re
import string
import urllib.parse
import zipfile
from typing import *

import requests

import onlinejudge._implementation.logging as log
import onlinejudge._implementation.utils as utils
import onlinejudge.dispatch
import onlinejudge.type
from onlinejudge.type import TestCase


class AOJService(onlinejudge.type.Service):
    def get_url(self) -> str:
        return 'http://judge.u-aizu.ac.jp/onlinejudge/'

    def get_name(self) -> str:
        return 'Aizu Online Judge'

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
    """
    :ivar problem_id: :py:class:`str` like `DSL_1_A` or `2256`
    """

    def __init__(self, problem_id):
        self.problem_id = problem_id

    def download_sample_cases(self, session: Optional[requests.Session] = None) -> List[TestCase]:
        session = session or utils.get_default_session()
        # get samples via the official API
        # reference: http://developers.u-aizu.ac.jp/api?key=judgedat%2Ftestcases%2Fsamples%2F%7BproblemId%7D_GET
        url = 'https://judgedat.u-aizu.ac.jp/testcases/samples/{}'.format(self.problem_id)
        resp = utils.request('GET', url, session=session)
        samples = []  # type: List[TestCase]
        for i, sample in enumerate(json.loads(resp.content.decode(resp.encoding))):
            samples += [TestCase(
                'sample-{}'.format(i + 1),
                str(sample['serial']),
                sample['in'].encode(),
                str(sample['serial']),
                sample['out'].encode(),
            )]
        return samples

    def download_system_cases(self, session: Optional[requests.Session] = None) -> List[TestCase]:
        session = session or utils.get_default_session()

        # get header
        # reference: http://developers.u-aizu.ac.jp/api?key=judgedat%2Ftestcases%2F%7BproblemId%7D%2Fheader_GET
        url = 'https://judgedat.u-aizu.ac.jp/testcases/{}/header'.format(self.problem_id)
        resp = utils.request('GET', url, session=session)
        header = json.loads(resp.content.decode(resp.encoding))

        # get testcases via the official API
        testcases = []  # type: List[TestCase]
        for header in header['headers']:
            # NOTE: the endpoints are not same to http://developers.u-aizu.ac.jp/api?key=judgedat%2Ftestcases%2F%7BproblemId%7D%2F%7Bserial%7D_GET since the json API often says "..... (terminated because of the limitation)"
            url = 'https://judgedat.u-aizu.ac.jp/testcases/{}/{}'.format(self.problem_id, header['serial'])
            resp_in = utils.request('GET', url + '/in', session=session)
            resp_out = utils.request('GET', url + '/out', session=session)
            testcases += [TestCase(
                header['name'],
                header['name'],
                resp_in.content,
                header['name'],
                resp_out.content,
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

        return None

    def get_service(self) -> AOJService:
        return AOJService()


class AOJArenaProblem(onlinejudge.type.Problem):
    """
    :ivar arena_id: :py:class:`str`. for example, `RitsCamp19Day2`
    :ivar alphabet: :py:class:`str`

    .. versionadded:: 6.1.0
    """

    def __init__(self, arena_id, alphabet):
        assert alphabet in string.ascii_uppercase
        self.arena_id = arena_id
        self.alphabet = alphabet

        self._problem_id = None  # Optional[str]

    def get_problem_id(self, session: Optional[requests.Session] = None) -> str:
        """
        :note: use http://developers.u-aizu.ac.jp/api?key=judgeapi%2Farenas%2F%7BarenaId%7D%2Fproblems_GET
        """

        if self._problem_id is None:
            session = session or utils.get_default_session()
            url = 'https://judgeapi.u-aizu.ac.jp/arenas/{}/problems'.format(self.arena_id)
            resp = utils.request('GET', url, session=session)
            problems = json.loads(resp.content.decode(resp.encoding))
            for problem in problems:
                if problem['id'] == self.alphabet:
                    self._problem_id = problem['problemId']
                    log.debug('problem: %s', problem)
                    break
        return self._problem_id

    def download_sample_cases(self, session: Optional[requests.Session] = None) -> List[TestCase]:
        log.warning("most of problems in arena have no registered sample cases.")
        return AOJProblem(self.get_problem_id()).download_sample_cases(session=session)

    def download_system_cases(self, session: Optional[requests.Session] = None) -> List[TestCase]:
        return AOJProblem(self.get_problem_id()).download_system_cases(session=session)

    def get_url(self) -> str:
        return 'https://onlinejudge.u-aizu.ac.jp/services/room.html#{}/problems/{}'.format(self.arena_id, self.alphabet)

    @classmethod
    def from_url(cls, url: str) -> Optional['AOJArenaProblem']:
        # example: https://onlinejudge.u-aizu.ac.jp/services/room.html#RitsCamp19Day2/problems/A
        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'onlinejudge.u-aizu.ac.jp' \
                and utils.normpath(result.path) == '/services/room.html':
            fragment = result.fragment.split('/')
            if len(fragment) == 3 and fragment[1] == 'problems':
                return cls(fragment[0], fragment[2].upper())
        return None

    def get_service(self) -> AOJService:
        return AOJService()


onlinejudge.dispatch.services += [AOJService]
onlinejudge.dispatch.problems += [AOJProblem, AOJArenaProblem]
