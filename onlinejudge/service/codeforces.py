# Python Version: 3.x
"""
the module for Codeforces (https://codeforces.com/)

:note: There is the offcial API https://codeforces.com/api/help
"""

import datetime
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

_CODEFORCES_DOMAINS = ('codeforces.com', 'm1.codeforces.com', 'm2.codeforces.com', 'm3.codeforces.com')


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

    def get_url_of_login_page(self) -> str:
        return 'https://codeforces.com/enter'

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
                and result.netloc in _CODEFORCES_DOMAINS:
            return cls()
        return None

    def iterate_contest_data(self, *, is_gym: bool = False, session: Optional[requests.Session] = None) -> Iterator['CodeforcesContestData']:
        session = session or utils.get_default_session()
        url = 'https://codeforces.com/api/contest.list?gym={}'.format('true' if is_gym else 'false')
        resp = utils.request('GET', url, session=session)
        timestamp = datetime.datetime.now(datetime.timezone.utc).astimezone()
        data = json.loads(resp.content.decode(resp.encoding))
        assert data['status'] == 'OK'
        for row in data['result']:
            yield CodeforcesContestData._from_json(row, response=resp, session=session, timestamp=timestamp)

    def iterate_contests(self, *, is_gym: bool = False, session: Optional[requests.Session] = None) -> Iterator['CodeforcesContest']:
        for data in self.iterate_contest_data(is_gym=is_gym, session=session):
            yield data.contest


class CodeforcesContestData(ContestData):
    # yapf: disable
    def __init__(
            self,
            *,
            contest: 'CodeforcesContest',
            duration_seconds: int,
            frozen: bool,
            name: str,
            phase: str,
            relative_time_seconds: int,
            response: requests.Response,
            session: requests.Session,
            start_time_seconds: int,
            timestamp: datetime.datetime,
            type: str  # TODO: in Python 3.5, you cannnot use both "*" and trailing ","
    ):
        # yapf: enable
        self._contest = contest
        self.duration_seconds = duration_seconds
        self.frozen = frozen
        self._name = name
        self.phase = phase
        self.relative_time_seconds = relative_time_seconds
        self._response = response
        self._session = session
        self.start_time_seconds = start_time_seconds
        self._timestamp = timestamp
        self.type = type

    @property
    def contest(self) -> 'CodeforcesContest':
        return self._contest

    @property
    def name(self) -> str:
        return self._name

    @property
    def json(self) -> bytes:
        return self._response.content

    @property
    def response(self) -> requests.Response:
        return self._response

    @property
    def session(self) -> requests.Session:
        return self._session

    @property
    def timestamp(self) -> datetime.datetime:
        return self._timestamp

    @classmethod
    def _from_json(cls, row: Dict[str, Any], *, response: requests.Response, session: requests.Session, timestamp: datetime.datetime) -> 'CodeforcesContestData':
        return CodeforcesContestData(
            contest=CodeforcesContest(contest_id=row['id']),
            duration_seconds=int(row['durationSeconds']),
            frozen=row['frozen'],
            name=row['name'],
            phase=row['phase'],
            relative_time_seconds=int(row['relativeTimeSeconds']),
            response=response,
            session=session,
            start_time_seconds=int(row['startTimeSeconds']),
            timestamp=timestamp,
            type=row['type'],
        )


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

    def get_url(self) -> str:
        return 'https://codeforces.com/{}/{}'.format(self.kind, self.contest_id)

    @classmethod
    def from_url(cls, url: str) -> Optional['CodeforcesContest']:
        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc in _CODEFORCES_DOMAINS:
            table = {}
            table['contest'] = r'/contest/([0-9]+).*'.format()  # example: https://codeforces.com/contest/538
            table['gym'] = r'/gym/([0-9]+).*'.format()  # example: https://codeforces.com/gym/101021
            for kind, expr in table.items():
                m = re.match(expr, utils.normpath(result.path))
                if m:
                    return cls(contest_id=int(m.group(1)), kind=kind)
        return None

    def get_service(self) -> CodeforcesService:
        return CodeforcesService()

    def list_problem_data(self, *, session: Optional[requests.Session] = None) -> List['CodeforcesProblemData']:
        session = session or utils.get_default_session()
        url = 'https://codeforces.com/api/contest.standings?contestId={}&from=1&count=1'.format(self.contest_id)
        resp = utils.request('GET', url, session=session)
        timestamp = datetime.datetime.now(datetime.timezone.utc).astimezone()
        data = json.loads(resp.content.decode(resp.encoding))
        assert data['status'] == 'OK'
        return [CodeforcesProblemData._from_json(row, response=resp, session=session, timestamp=timestamp) for row in data['result']['problems']]

    def list_problems(self, *, session: Optional[requests.Session] = None) -> Sequence['CodeforcesProblem']:
        return tuple([data.problem for data in self.list_problem_data(session=session)])

    def download_data(self, *, session: Optional[requests.Session] = None) -> CodeforcesContestData:
        session = session or utils.get_default_session()
        url = 'https://codeforces.com/api/contest.standings?contestId={}&from=1&count=1'.format(self.contest_id)
        resp = utils.request('GET', url, session=session)
        timestamp = datetime.datetime.now(datetime.timezone.utc).astimezone()
        data = json.loads(resp.content.decode(resp.encoding))
        assert data['status'] == 'OK'
        return CodeforcesContestData._from_json(data['result']['contest'], response=resp, session=session, timestamp=timestamp)


class CodeforcesProblemData(ProblemData):
    # yapf: disable
    def __init__(
            self,
            *,
            name: str,
            points: Optional[int],
            problem: 'CodeforcesProblem',
            rating: Optional[int],
            response: requests.Response,
            session: requests.Session,
            tags: List[str],
            timestamp: datetime.datetime,
            type: str  # TODO: in Python 3.5, you cannnot use both "*" and trailing ","
    ):
        # yapf: enable
        self._name = name
        self.points = points
        self._problem = problem
        self.rating = rating
        self._response = response
        self._session = session
        self.tags = tags
        self._timestamp = timestamp
        self.type = type

    @property
    def problem(self) -> 'CodeforcesProblem':
        return self._problem

    @property
    def name(self) -> str:
        return self._name

    @property
    def json(self) -> bytes:
        return self._response.content

    @property
    def response(self) -> requests.Response:
        return self._response

    @property
    def session(self) -> requests.Session:
        return self._session

    @property
    def timestamp(self) -> datetime.datetime:
        return self._timestamp

    @classmethod
    def _from_json(cls, row: Dict[str, Any], response: requests.Response, session: requests.Session, timestamp: datetime.datetime) -> 'CodeforcesProblemData':
        return CodeforcesProblemData(
            name=row['name'],
            points=(int(row['points']) if 'points' in row else None),
            problem=CodeforcesProblem(contest_id=row['contestId'], index=row['index']),
            rating=(int(row['rating']) if 'rating' in row else None),
            response=response,
            session=session,
            tags=row['tags'],
            timestamp=timestamp,
            type=row['type'],
        )


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

    def download_sample_cases(self, *, session: Optional[requests.Session] = None) -> List[onlinejudge.type.TestCase]:
        session = session or utils.get_default_session()
        # get
        resp = utils.request('GET', self.get_url(), session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        samples = onlinejudge._implementation.testcase_zipper.SampleZipper()
        for tag in soup.find_all('div', class_=re.compile('^(in|out)put$')):  # Codeforces writes very nice HTML :)
            log.debug('tag: %s', str(tag))
            assert len(list(tag.children)) == 2  # if not 2, next line throws ValueError.
            title, pre = list(tag.children)
            assert 'title' in title.attrs['class']
            assert pre.name == 'pre'
            s = utils.parse_content(pre)
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
                and result.netloc in _CODEFORCES_DOMAINS:
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

    def download_data(self, *, session: Optional[requests.Session] = None) -> CodeforcesProblemData:
        for data in self.get_contest().list_problem_data(session=session):
            if data.problem.get_url() == self.get_url():
                return data
        assert False


onlinejudge.dispatch.services += [CodeforcesService]
onlinejudge.dispatch.contests += [CodeforcesContest]
onlinejudge.dispatch.problems += [CodeforcesProblem]
