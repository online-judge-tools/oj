# Python Version: 3.x
"""
the module for Toph (https://toph.co/)
"""

import posixpath
import re
import string
import urllib.parse
from typing import *

import bs4
import requests

import onlinejudge._implementation.logging as log
import onlinejudge._implementation.testcase_zipper
import onlinejudge._implementation.utils as utils
import onlinejudge.dispatch
import onlinejudge.type
from onlinejudge.type import *


class TophService(onlinejudge.type.Service):
    def login(self, get_credentials: onlinejudge.type.CredentialsProvider, session: Optional[requests.Session] = None) -> None:
        """
        :raises LoginError:
        """
        session = session or utils.get_default_session()
        url = 'https://toph.co/login'
        # get
        resp = utils.request('GET', url, session=session)
        if resp.url != url:  # redirected
            log.info('You are already logged in.')
            return
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        form = soup.find('form', class_='login-form')
        log.debug('form: %s', str(form))
        username, password = get_credentials()
        form['action'] = '/login'  # to avoid KeyError inside form.request method as Toph does not have any defined action
        form = utils.FormSender(form, url=resp.url)
        form.set('handle', username)
        form.set('password', password)
        # post
        resp = form.request(session)
        resp.raise_for_status()

        resp = utils.request('GET', url, session=session)  # Toph's Location header is not getting the expected value
        if resp.url != url:
            log.success('Welcome, %s.', username)
        else:
            log.failure('Invalid handle/email or password.')
            raise LoginError('Invalid handle/email or password.')

    def is_logged_in(self, session: Optional[requests.Session] = None) -> bool:
        session = session or utils.get_default_session()
        url = 'https://toph.co/login'
        resp = utils.request('GET', url, session=session, allow_redirects=False)
        return resp.status_code != 200

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
    """
    :ivar problem_id: :py:class:`str`
    :ivar contest_id: :py:class:`Optional` [ :py:class:`str` ]
    """

    def __init__(self, problem_id: str, contest_id: Optional[str] = None):
        assert isinstance(problem_id, str)
        if contest_id is not None:
            raise NotImplementedError
        self.problem_id = problem_id

    def download_sample_cases(self, session: Optional[requests.Session] = None) -> List[onlinejudge.type.TestCase]:
        session = session or utils.get_default_session()
        resp = utils.request('GET', self.get_url(), session=session)
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        samples = onlinejudge._implementation.testcase_zipper.SampleZipper()
        for table in soup.find_all('table', class_="samples"):
            log.debug('table: %s', str(table))
            case = table.find('tbody').find('tr')
            assert len(list(case.children))
            input_pre, output_pre = list(map(lambda td: td.find('pre'), list(case.children)))
            assert input_pre.name == 'pre'
            assert output_pre.name == 'pre'
            assert re.search("^preSample.*Input$", input_pre.attrs['id'])
            assert re.search("^preSample.*Output$", output_pre.attrs['id'])
            samples.add(input_pre.text.lstrip().encode(), "Input")
            samples.add(output_pre.text.lstrip().encode(), "Output")
        return samples.get()

    def get_available_languages(self, session: Optional[requests.Session] = None) -> List[Language]:
        """
        :raises NotImplementedError:
        """
        session = session or utils.get_default_session()
        # get
        resp = utils.request('GET', self.get_url(), session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        select = soup.find('select', attrs={'name': 'languageId'})
        if select is None:
            raise NotLoggedInError
        languages = []  # type: List[Language]
        for option in select.findAll('option'):
            languages += [Language(LanguageId(option.attrs['value']), option.string.strip())]
        return languages

    def submit_code(self, code: bytes, language_id: LanguageId, filename: Optional[str] = None, session: Optional[requests.Session] = None) -> Submission:
        """
        :raises NotImplementedError:
        :raises SubmissionError:
        """
        session = session or utils.get_default_session()
        # get
        resp = utils.request('GET', self.get_url(), session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        form = soup.find('form')
        if form is None:
            log.error('not logged in')
            raise LoginError
        log.debug('form: %s', str(form))
        if form.find('select') and form.find('select').attrs['name'] != 'languageId':
            log.error("Wrong submission URL")
            raise SubmissionError

        # make data
        form = utils.FormSender(form, url=resp.url)
        form.set('languageId', language_id)
        form.set_file('source', 'code', code)
        resp = form.request(session=session)
        resp.raise_for_status()
        # result
        if '/s/' in resp.url:
            # example: https://toph.co/s/201410
            log.success('success: result: %s', resp.url)
            return utils.DummySubmission(resp.url, problem=self)
        else:
            log.failure('failure')
            log.debug('redirected to %s', resp.url)
            raise SubmissionError

    def get_url(self) -> str:
        # TODO: Check for contest_id to return the appropriate  URL when support for contest is added
        return 'https://toph.co/p/{}'.format(self.problem_id)

    def get_service(self) -> TophService:
        return TophService()

    @classmethod
    def from_url(cls, s: str) -> Optional['TophProblem']:
        result = urllib.parse.urlparse(s)
        dirname, basename = posixpath.split(utils.normpath(result.path))
        # example: https://toph.co/p/new-year-couple
        if result.scheme in ('', 'http', 'https') \
                and result.netloc.count('.') == 1 \
                and result.netloc.endswith('toph.co') \
                and dirname == '/p' \
                and basename:
            problem_id = basename
            return cls(problem_id)

        return None


onlinejudge.dispatch.services += [TophService]
onlinejudge.dispatch.problems += [TophProblem]
