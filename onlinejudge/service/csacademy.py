# Python Version: 3.x
"""
the module for CS Academy (https://csacademy.com/)
"""

import json
import posixpath
import re
import urllib.parse
from typing import *

import requests

import onlinejudge._implementation.logging as log
import onlinejudge._implementation.utils as utils
import onlinejudge.dispatch
import onlinejudge.type
from onlinejudge.type import TestCase


class CSAcademyService(onlinejudge.type.Service):
    def get_url(self) -> str:
        return 'https://csacademy.com/'

    def get_name(self) -> str:
        return 'CS Academy'

    @classmethod
    def from_url(cls, url: str) -> Optional['CSAcademyService']:
        # example: https://csacademy.com/
        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc in ('csacademy.com', 'www.csacademy.com'):
            return cls()
        return None


class CSAcademyProblem(onlinejudge.type.Problem):
    def __init__(self, contest_name: str, task_name: str):
        self.contest_name = contest_name
        self.task_name = task_name

    def download_sample_cases(self, session: Optional[requests.Session] = None) -> List[TestCase]:
        session = session or utils.get_default_session()
        base_url = self.get_url()

        # get csrftoken
        resp = utils.request('GET', base_url, session=session)
        csrftoken = None
        for cookie in session.cookies:
            if cookie.name == 'csrftoken' and cookie.domain == 'csacademy.com':  # type: ignore
                csrftoken = cookie.value  # type: ignore
        if csrftoken is None:
            log.error('csrftoken is not found')
            return []

        # get config
        headers = {
            'x-csrftoken': csrftoken,
            'x-requested-with': 'XMLHttpRequest',
        }
        contest_url = 'https://csacademy.com/contest/{}/'.format(self.contest_name)
        resp = utils.request('GET', contest_url, session=session, headers=headers)
        # parse config
        assert resp.encoding is None
        config = json.loads(resp.content.decode())  # NOTE: Should I memoize this? Is the CSAcademyRound class required?
        task_config = None
        for it in config['state']['contesttask']:
            if it['name'] == self.task_name:
                task_config = it
        if task_config is None:
            log.error('no such task: %s', self.task_name)
            return []

        # get
        get_contest_task_url = 'https://csacademy.com/contest/get_contest_task/'
        payload = {'contestTaskId': (None, str(task_config['id']))}
        headers = {
            'x-csrftoken': csrftoken,
            'x-requested-with': 'XMLHttpRequest',
            'Referer': base_url,
        }
        resp = utils.request('POST', get_contest_task_url, session=session, files=payload, headers=headers)
        # parse
        assert resp.encoding is None
        contest_task = json.loads(resp.content.decode())  # NOTE: Should I memoize this?
        if contest_task.get('title') == 'Page not found':
            log.error('something wrong')
            return []
        samples = []
        for test_number, example_test in enumerate(contest_task['state']['EvalTask'][0]['exampleTests']):
            inname = 'Input {}'.format(test_number)
            outname = 'Output {}'.format(test_number)
            samples += [TestCase(
                'sample-{}'.format(test_number + 1),
                inname,
                example_test['input'].encode(),
                outname,
                example_test['output'].encode(),
            )]
        return samples

    def get_url(self) -> str:
        return 'https://csacademy.com/content/{}/task/{}/'.format(self.contest_name, self.task_name)

    def get_service(self) -> CSAcademyService:
        return CSAcademyService()

    @classmethod
    def from_url(cls, url: str) -> Optional['CSAcademyProblem']:
        # example: https://csacademy.com/contest/round-38/task/path-union/
        # example: https://csacademy.com/contest/round-38/task/path-union/discussion/
        # example: https://csacademy.com/contest/archive/task/swap_permutation/
        # example: https://csacademy.com/contest/archive/task/swap_permutation/statement/
        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc in ('csacademy.com', 'www.csacademy.com'):
            m = re.match(r'^/contest/([0-9A-Za-z_-]+)/task/([0-9A-Za-z_-]+)(|/statement|/solution|/discussion|/statistics|/submissions)/?$', utils.normpath(result.path))
            if m:
                return cls(m.group(1), m.group(2))
        return None


onlinejudge.dispatch.services += [CSAcademyService]
onlinejudge.dispatch.problems += [CSAcademyProblem]
