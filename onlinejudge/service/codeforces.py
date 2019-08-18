# Python Version: 3.x
"""
the module for Codeforces (https://codeforces.com/)

:note: There is the offcial API https://codeforces.com/api/help
"""

import json
import re
import string
import urllib.parse
from typing import *

import bs4

import onlinejudge._implementation.logging as log
import onlinejudge._implementation.testcase_zipper
import onlinejudge._implementation.utils as utils
import onlinejudge.dispatch
import onlinejudge.type
from onlinejudge.type import *


class CodeforcesService(onlinejudge.type.Service):
    def login(self, *, get_credentials: onlinejudge.type.CredentialsProvider, session: Optional[requests.Session] = None) -> None:
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

    def is_logged_in(self, *, session: Optional[requests.Session] = None) -> bool:
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

    def iterate_contest_contents(self, *, is_gym: bool = False, session: Optional[requests.Session] = None) -> Iterator['CodeforcesContestContent']:
        session = session or utils.get_default_session()
        url = 'https://codeforces.com/api/contest.list?gym={}'.format('true' if is_gym else 'false')
        resp = utils.request('GET', url, session=session)
        data = json.loads(resp.content.decode(resp.encoding))
        assert data['status'] == 'OK'
        for row in data['result']:
            yield CodeforcesContest._from_json(row)

    def iterate_contests(self, *, is_gym: bool = False, session: Optional[requests.Session] = None) -> Iterator['CodeforcesContest']:
        for content in self.iterate_contest_contents(is_gym=is_gym, session=session):
            yield content.contest


# TODO: use the new style of NamedTuple added from Pyhon 3.6
CodeforcesContestContent = NamedTuple('CodeforcesProblemContent', [
    ('contest', 'CodeforcesContest'),
    ('duration_seconds', int),
    ('frozen', bool),
    ('name', str),
    ('phase', str),
    ('relative_time_seconds', int),
    ('start_time_seconds', int),
    ('type', str),
])


class CodeforcesContest(onlinejudge.type.Contest):
    """
    :ivar contest_id: :py:class:`int`
    :ivar kind: :py:class:`str` must be `contest` or `gym`
    """
    def __init__(self, *, contest_id: int, kind: Optional[str] = None):
        assert kind in (None, 'contest', 'gym')
        self.contest_id = contest_id
        if kind is None:
            if self.contest_id < 100000:
                kind = 'contest'
            else:
                kind = 'gym'
        self.kind = kind

    @classmethod
    def from_url(cls, url: str) -> Optional['CodeforcesContest']:
        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'codeforces.com':
            table = {}
            table['contest'] = r'/contest/([0-9]+).*'.format()  # example: https://codeforces.com/contest/538
            table['gym'] = r'/gym/([0-9]+).*'.format()  # example: https://codeforces.com/gym/101021
            for kind, expr in table.items():
                m = re.match(expr, utils.normpath(result.path))
                if m:
                    return cls(contest_id=int(m.group(1)), kind=kind)
        return None

    @classmethod
    def _from_json(cls, row: Dict[str, Any]) -> CodeforcesContestContent:
        self = cls(contest_id=row['id'])
        return CodeforcesContestContent(
            contest=self,
            duration_seconds=int(row['durationSeconds']),
            frozen=row['frozen'],
            name=row['name'],
            phase=row['phase'],
            relative_time_seconds=int(row['relativeTimeSeconds']),
            start_time_seconds=int(row['startTimeSeconds']),
            type=row['type'],
        )

    def list_problem_contents(self, *, session: Optional[requests.Session] = None) -> List['CodeforcesProblemContent']:
        session = session or utils.get_default_session()
        url = 'https://codeforces.com/api/contest.standings?contestId={}&from=1&count=1'.format(self.contest_id)
        resp = utils.request('GET', url, session=session)
        data = json.loads(resp.content.decode(resp.encoding))
        assert data['status'] == 'OK'
        return [CodeforcesProblem._from_json(row) for row in data['result']['problems']]

    # TODO: why is "type: ignore" required?
    def list_problems(self, *, session: Optional[requests.Session] = None) -> List['CodeforcesProblem']:  # type: ignore
        return [content.problem for content in self.list_problem_contents(session=session)]

    def download_content(self, *, session: Optional[requests.Session] = None) -> CodeforcesContestContent:
        session = session or utils.get_default_session()
        url = 'https://codeforces.com/api/contest.standings?contestId={}&from=1&count=1'.format(self.contest_id)
        resp = utils.request('GET', url, session=session)
        data = json.loads(resp.content.decode(resp.encoding))
        assert data['status'] == 'OK'
        return CodeforcesContest._from_json(data['result']['contest'])


# TODO: use the new style of NamedTuple added from Pyhon 3.6
CodeforcesProblemContent = NamedTuple('CodeforcesProblemContent', [
    ('name', str),
    ('points', Optional[int]),
    ('problem', 'CodeforcesProblem'),
    ('rating', int),
    ('tags', List[str]),
    ('type', str),
])


# NOTE: Codeforces has its API: https://codeforces.com/api/help
class CodeforcesProblem(onlinejudge.type.Problem):
    """
    :ivar contest_id: :py:class:`int`
    :ivar index: :py:class:`str`
    :ivar kind: :py:class:`str` must be `contest` or `gym`
    """
    def __init__(self, *, contest_id: int, index: str, kind: Optional[str] = None):
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

    @classmethod
    def _from_json(cls, row: Dict[str, Any]) -> CodeforcesProblemContent:
        self = cls(contest_id=row['contestId'], index=row['index'])
        return CodeforcesProblemContent(
            name=row['name'],
            points=(int(row['points']) if 'points' in row else None),
            problem=self,
            rating=int(row['rating']),
            tags=row['tags'],
            type=row['type'],
        )

    def download_sample_cases(self, *, session: Optional[requests.Session] = None) -> List[onlinejudge.type.TestCase]:
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

    def get_available_languages(self, *, session: Optional[requests.Session] = None) -> List[Language]:
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

    def submit_code(self, code: bytes, language_id: LanguageId, *, filename: Optional[str] = None, session: Optional[requests.Session] = None) -> onlinejudge.type.Submission:
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

    def get_contest(self) -> CodeforcesContest:
        assert self.kind != 'problemset'
        return CodeforcesContest(contest_id=self.contest_id, kind=self.kind)

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
                    return cls(contest_id=int(m.group(1)), index=index, kind=kind)
        return None

    def download_content(self, *, session: Optional[requests.Session] = None) -> CodeforcesProblemContent:
        for content in self.get_contest().list_problem_contents(session=session):
            if content.problem.get_url() == self.get_url():
                return content
        assert False


onlinejudge.dispatch.services += [CodeforcesService]
onlinejudge.dispatch.contests += [CodeforcesContest]
onlinejudge.dispatch.problems += [CodeforcesProblem]
