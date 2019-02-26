# Python Version: 3.x
import posixpath
import re
import string
import urllib.parse
from typing import *

import bs4
import requests

import onlinejudge.dispatch
import onlinejudge.implementation.logging as log
import onlinejudge.implementation.utils as utils
import onlinejudge.type
from onlinejudge.type import SubmissionError


@utils.singleton
class TophService(onlinejudge.type.Service):
    def login(self, get_credentials: onlinejudge.type.CredentialsProvider, session: Optional[requests.Session] = None) -> bool:
        session = session or utils.new_default_session()
        url = 'https://toph.co/login'
        # get
        resp = utils.request('GET', url, session=session)
        if resp.url != url:  # redirected
            log.info('You are already logged in.')
            return True
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
            return True
        else:
            log.failure('Invalid handle/email or password.')
            return False

    def is_logged_in(self, session: Optional[requests.Session] = None) -> bool:
        session = session or utils.new_default_session()
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
    def __init__(self, problem_id: str, contest_id: Optional[str] = None):
        assert isinstance(problem_id, str)
        if contest_id is not None:
            raise NotImplementedError
        self.problem_id = problem_id

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

    def get_language_dict(self, session: Optional['requests.Session'] = None) -> Dict[str, onlinejudge.type.Language]:
        session = session or utils.new_default_session()
        # get
        resp = utils.request('GET', self.get_url(), session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        select = soup.find('select', attrs={'name': 'languageId'})
        if select is None:
            log.error('not logged in')
            return {}
        language_dict = {}
        for option in select.findAll('option'):
            language_dict[option.attrs['value']] = {'description': option.string.strip()}
        return language_dict

    def submit_code(self, code: bytes, language: str, session: Optional['requests.Session'] = None) -> onlinejudge.type.Submission:  # or SubmissionError
        session = session or utils.new_default_session()
        # get
        resp = utils.request('GET', self.get_url(), session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        form = soup.find('form')
        if form is None:
            log.error('not logged in')
            raise SubmissionError
        log.debug('form: %s', str(form))
        if form.find('select') and form.find('select').attrs['name'] != 'languageId':
            log.error("Wrong submission URL")
            raise SubmissionError

        # make data
        form = utils.FormSender(form, url=resp.url)
        form.set('languageId', language)
        form.set_file('source', 'code', code)
        resp = form.request(session=session)
        resp.raise_for_status()
        # result
        if '/s/' in resp.url:
            # example: https://toph.co/s/201410
            log.success('success: result: %s', resp.url)
            return onlinejudge.type.DummySubmission(resp.url)
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
