# Python Version: 3.x
"""
the module for Codeforces (https://codeforces.com/)

:note: There is the offcial API https://codeforces.com/api/help
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


class CodeforcesService(onlinejudge.type.Service):
    def login(self, get_credentials: onlinejudge.type.CredentialsProvider, session: Optional[requests.Session] = None) -> None:
        """
        :raises LoginError:
        """
        session = session or utils.get_default_session()
        url = 'https://codeforces.com/enter'
        # get
        resp = utils.request('GET', url, session=session)
        if resp.url != url:  # redirected
            log.info('You have already signed in.')
            return
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        form = soup.find('form', id='enterForm')
        log.debug('form: %s', str(form))
        username, password = get_credentials()
        form = utils.FormSender(form, url=resp.url)
        form.set('handleOrEmail', username)
        form.set('password', password)
        form.set('remember', 'on')
        # post
        resp = form.request(session)
        resp.raise_for_status()
        if resp.url != url:  # redirected
            log.success('Welcome, %s.', username)
        else:
            log.failure('Invalid handle or password.')
            raise LoginError('Invalid handle or password.')

    def is_logged_in(self, session: Optional[requests.Session] = None) -> bool:
        session = session or utils.get_default_session()
        url = 'https://codeforces.com/enter'
        resp = utils.request('GET', url, session=session, allow_redirects=False)
        return resp.status_code == 302

    def get_url(self) -> str:
        return 'https://codeforces.com/'

    def get_name(self) -> str:
        return 'Codeforces'

    @classmethod
    def from_url(cls, url: str) -> Optional['CodeforcesService']:
        # example: https://codeforces.com/
        # example: http://codeforces.com/
        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'codeforces.com':
            return cls()
        return None


# NOTE: Codeforces has its API: https://codeforces.com/api/help
class CodeforcesProblem(onlinejudge.type.Problem):
    """
    :ivar contest_id: :py:class:`int`
    :ivar index: :py:class:`str`
    :ivar kind: :py:class:`str` must be `contest` or `gym`
    """

    def __init__(self, contest_id: int, index: str, kind: Optional[str] = None):
        assert isinstance(contest_id, int)
        assert 1 <= len(index) <= 2
        assert index[0] in string.ascii_uppercase
        if len(index) == 2:
            assert index[1] in string.digits
        assert kind in (None, 'contest', 'gym', 'problemset')
        self.contest_id = contest_id
        self.index = index
        if kind is None:
            if self.contest_id < 100000:
                kind = 'contest'
            else:
                kind = 'gym'
        self.kind = kind  # It seems 'gym' is specialized, 'contest' and 'problemset' are the same thing

    def download_sample_cases(self, session: Optional[requests.Session] = None) -> List[onlinejudge.type.TestCase]:
        session = session or utils.get_default_session()
        # get
        resp = utils.request('GET', self.get_url(), session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        samples = onlinejudge._implementation.testcase_zipper.SampleZipper()
        for tag in soup.find_all('div', class_=re.compile('^(in|out)put$')):  # Codeforces writes very nice HTML :)
            log.debug('tag: %s', str(tag))
            assert len(list(tag.children))
            title, pre = list(tag.children)
            assert 'title' in title.attrs['class']
            assert pre.name == 'pre'
            s = ''
            for it in pre.children:
                if it.name == 'br':
                    s += '\n'
                else:
                    s += it.string
            s = s.lstrip()
            samples.add(s.encode(), title.string)
        return samples.get()

    def get_available_languages(self, session: Optional[requests.Session] = None) -> List[Language]:
        """
        :raises NotLoggedInError:
        """

        session = session or utils.get_default_session()
        # get
        resp = utils.request('GET', self.get_url(), session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        select = soup.find('select', attrs={'name': 'programTypeId'})
        if select is None:
            raise NotLoggedInError
        languages = []  # type: List[Language]
        for option in select.findAll('option'):
            languages += [Language(option.attrs['value'], option.string)]
        return languages

    def submit_code(self, code: bytes, language_id: LanguageId, filename: Optional[str] = None, session: Optional[requests.Session] = None) -> onlinejudge.type.Submission:
        """
        :raises NotLoggedInError:
        :raises SubmissionError:
        """

        session = session or utils.get_default_session()
        # get
        resp = utils.request('GET', self.get_url(), session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        form = soup.find('form', class_='submitForm')
        if form is None:
            log.error('not logged in')
            raise NotLoggedInError
        log.debug('form: %s', str(form))
        # make data
        form = utils.FormSender(form, url=resp.url)
        form.set('programTypeId', language_id)
        form.set_file('sourceFile', filename or 'code', code)
        resp = form.request(session=session)
        resp.raise_for_status()
        # result
        if resp.url.endswith('/my'):
            # example: https://codeforces.com/contest/598/my
            log.success('success: result: %s', resp.url)
            return utils.DummySubmission(resp.url, problem=self)
        else:
            log.failure('failure')
            # parse error messages
            soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
            msgs = []  # type: List[str]
            for span in soup.findAll('span', class_='error'):
                msgs += [span.string]
                log.warning('Codeforces says: "%s"', span.string)
            raise SubmissionError('it may be the "You have submitted exactly the same code before" error: ' + str(msgs))

    def get_url(self) -> str:
        table = {}
        table['contest'] = 'https://codeforces.com/contest/{}/problem/{}'
        table['problemset'] = 'https://codeforces.com/problemset/problem/{}/{}'
        table['gym'] = 'https://codeforces.com/gym/{}/problem/{}'
        return table[self.kind].format(self.contest_id, self.index)

    def get_service(self) -> CodeforcesService:
        return CodeforcesService()

    @classmethod
    def from_url(cls, url: str) -> Optional['CodeforcesProblem']:
        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'codeforces.com':
            # "0" is needed. example: https://codeforces.com/contest/1000/problem/0
            # "[1-9]?" is sometime used. example: https://codeforces.com/contest/1133/problem/F2
            re_for_index = r'(0|[A-Za-z][1-9]?)'
            table = {}
            table['contest'] = r'^/contest/([0-9]+)/problem/{}$'.format(re_for_index)  # example: https://codeforces.com/contest/538/problem/H
            table['problemset'] = r'^/problemset/problem/([0-9]+)/{}$'.format(re_for_index)  # example: https://codeforces.com/problemset/problem/700/B
            table['gym'] = r'^/gym/([0-9]+)/problem/{}$'.format(re_for_index)  # example: https://codeforces.com/gym/101021/problem/A
            for kind, expr in table.items():
                m = re.match(expr, utils.normpath(result.path))
                if m:
                    if m.group(2) == '0':
                        index = 'A'  # NOTE: This is broken if there was "A1".
                    else:
                        index = m.group(2).upper()
                    return cls(int(m.group(1)), index, kind=kind)
        return None


onlinejudge.dispatch.services += [CodeforcesService]
onlinejudge.dispatch.problems += [CodeforcesProblem]
