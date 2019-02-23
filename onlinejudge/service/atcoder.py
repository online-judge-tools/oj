# Python Version: 3.x
# -*- coding: utf-8 -*-
"""
the module for AtCoder (https://atcoder.jp/)
"""

import datetime
import itertools
import json
import posixpath
import re
import urllib.parse
from typing import *

import bs4
import requests

import onlinejudge.dispatch
import onlinejudge.implementation.logging as log
import onlinejudge.implementation.utils as utils
import onlinejudge.type
from onlinejudge.type import SubmissionError


def _request(*args, **kwargs):
    """
    This is a workaround. AtCoder's servers sometime fail to send "Content-Type" field.
    see https://github.com/kmyk/online-judge-tools/issues/28 and https://github.com/kmyk/online-judge-tools/issues/232
    """
    resp = utils.request(*args, **kwargs)
    log.debug('AtCoder\'s server said "Content-Type: %s"', resp.headers.get('Content-Type', '(not sent)'))
    resp.encoding = 'UTF-8'
    return resp


@utils.singleton
class AtCoderService(onlinejudge.type.Service):
    def login(self, get_credentials: onlinejudge.type.CredentialsProvider, session: Optional[requests.Session] = None) -> bool:
        session = session or utils.new_default_session()
        url = 'https://practice.contest.atcoder.jp/login'
        # get
        resp = _request('GET', url, session=session, allow_redirects=False)
        msgs = AtCoderService._get_messages_from_cookie(resp.cookies)
        for msg in msgs:
            log.status('message: %s', msg)
        if msgs:
            return 'login' not in resp.url
        # post
        username, password = get_credentials()
        resp = _request('POST', url, session=session, data={'name': username, 'password': password}, allow_redirects=False)
        msgs = AtCoderService._get_messages_from_cookie(resp.cookies)
        AtCoderService._report_messages(msgs)
        return 'login' not in resp.url  # AtCoder redirects to the top page if success

    def is_logged_in(self, session: Optional[requests.Session] = None) -> bool:
        session = session or utils.new_default_session()
        url = 'https://practice.contest.atcoder.jp/login'
        resp = _request('GET', url, session=session, allow_redirects=False)
        msgs = AtCoderService._get_messages_from_cookie(resp.cookies)
        return bool(msgs)

    def get_url(self) -> str:
        return 'https://atcoder.jp/'

    def get_name(self) -> str:
        return 'atcoder'

    @classmethod
    def from_url(cls, url: str) -> Optional['AtCoderService']:
        """
        :param url: example:

        -   https://atcoder.jp/
        -   http://agc012.contest.atcoder.jp/
        """

        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and (result.netloc in ('atcoder.jp', 'beta.atcoder.jp') or result.netloc.endswith('.contest.atcoder.jp')):
            return cls()
        return None

    @classmethod
    def _get_messages_from_cookie(cls, cookies) -> List[str]:
        msgtags = []  # type: List[str]
        for cookie in cookies:
            log.debug('cookie: %s', str(cookie))
            if cookie.name.startswith('__message_'):
                msg = json.loads(urllib.parse.unquote_plus(cookie.value))
                msgtags += [msg['c']]
                log.debug('message: %s: %s', cookie.name, str(msg))
        msgs = []  # type: List[str]
        for msgtag in msgtags:
            soup = bs4.BeautifulSoup(msgtag, utils.html_parser)
            msg = None
            for tag in soup.find_all():
                if tag.string and tag.string.strip():
                    msg = tag.string
                    break
            if msg is None:
                log.error('failed to parse message')
            else:
                msgs += [msg]
        return msgs

    @classmethod
    def _report_messages(cls, msgs: List[str], unexpected: bool = False) -> bool:
        for msg in msgs:
            log.status('message: %s', msg)
        if msgs and unexpected:
            log.failure('unexpected messages found')
        return bool(msgs)

    def iterate_contests(self, lang: str = 'ja', session: Optional[requests.Session] = None) -> Generator['AtCoderContest', None, None]:
        """
        :param lang: must be `ja` (default) or `en`.
        :note: `lang=ja` is required to see some Japanese-local contests.
        :note: You can use `lang=en` to see the English names of contests.
        """

        assert lang in ('ja', 'en')
        session = session or utils.new_default_session()
        last_page = None
        for page in itertools.count(1):  # 1-based
            if last_page is not None and page > last_page:
                break
            # get
            url = 'https://atcoder.jp/contests/archive?lang={}&page={}'.format(lang, page)
            resp = _request('GET', url, session=session)
            # parse
            soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
            if last_page is None:
                last_page = int(soup.find('ul', class_='pagination').find_all('li')[-1].text)
                log.debug('last page: %s', last_page)
            tbody = soup.find('tbody')
            for tr in tbody.find_all('tr'):
                yield AtCoderContest._from_table_row(tr, lang=lang)

    def get_user_history_url(self, user_id: str) -> str:
        return 'https://atcoder.jp/users/{}/history/json'.format(user_id)


class AtCoderContest(object):
    """
    :ivar contest_id: :py:class:`str`
    """

    def __init__(self, contest_id: str):
        self.contest_id = contest_id

        # NOTE: some fields remain undefined, comparing `_from_table_row`
        self._start_time_url = None  # type: Optional[str]
        self._contest_name_ja = None  # type: Optional[str]
        self._contest_name_en = None  # type: Optional[str]
        self._duration_text = None  # type: Optional[str]
        self._rated_range = None  # type: Optional[str]

    @classmethod
    def from_url(cls, url: str) -> Optional['AtCoderContest']:
        """
        :param url: example:

        -   https://kupc2014.contest.atcoder.jp/tasks/kupc2014_d
        -   https://atcoder.jp/contests/agc030
        """

        result = urllib.parse.urlparse(url)

        # example: https://kupc2014.contest.atcoder.jp/tasks/kupc2014_d
        if result.scheme in ('', 'http', 'https') and result.hostname.endswith('.contest.atcoder.jp'):
            contest_id = utils.remove_suffix(result.hostname, '.contest.atcoder.jp')
            return cls(contest_id)

        # example: https://atcoder.jp/contests/agc030
        if result.scheme in ('', 'http', 'https') and result.hostname in ('atcoder.jp', 'beta.atcoder.jp'):
            m = re.match(r'^/contests/([\w\-_]+)/?$', utils.normpath(result.path))
            if m:
                contest_id = m.group(1)
                return cls(contest_id)

        return None

    @classmethod
    def _from_table_row(cls, tr: bs4.Tag, lang: str) -> 'AtCoderContest':
        tds = tr.find_all('td')
        assert len(tds) == 4
        anchors = [tds[0].find('a'), tds[1].find('a')]
        contest_path = anchors[1]['href']
        assert contest_path.startswith('/contests/')
        contest_id = contest_path[len('/contests/'):]
        self = AtCoderContest(contest_id)
        self._start_time_url = anchors[0]['href']
        if lang == 'ja':
            self._contest_name_ja = anchors[1].text
        elif lang == 'en':
            self._contest_name_en = anchors[1].text
        else:
            assert False
        self._duration_text = tds[2].text
        self._rated_range = tds[3].text
        return self

    def get_start_time(self) -> datetime.datetime:
        if self._start_time_url is None:
            raise NotImplementedError
        # TODO: we need to use an ISO-format parser
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self._start_time_url).query)
        assert len(query['iso']) == 1
        assert query['p1'] == ['248']  # means JST
        return datetime.datetime.strptime(query['iso'][0], '%Y%m%dT%H%M').replace(tzinfo=utils.tzinfo_jst)

    def get_contest_name(self, lang: Optional[str] = None) -> str:
        if lang is None:
            if self._contest_name_en is not None:
                return self._contest_name_en
            elif self._contest_name_ja is not None:
                return self._contest_name_ja
            else:
                raise NotImplementedError
        elif lang == 'en':
            if self._contest_name_en is None:
                raise NotImplementedError
            return self._contest_name_en
        elif lang == 'ja':
            if self._contest_name_ja is None:
                raise NotImplementedError
            return self._contest_name_ja
        else:
            assert False

    def get_duration(self) -> datetime.timedelta:
        if self._duration_text is None:
            raise NotImplementedError
        hours, minutes = map(int, self._duration_text.split(':'))
        return datetime.timedelta(hours=hours, minutes=minutes)

    def get_rated_range(self) -> str:
        if self._rated_range is None:
            raise NotImplementedError
        return self._rated_range

    def list_problems(self, session: Optional[requests.Session] = None) -> List['AtCoderProblem']:
        # get
        session = session or utils.new_default_session()
        url = 'https://atcoder.jp/contests/{}/tasks'.format(self.contest_id)
        resp = _request('GET', url, session=session)

        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        tbody = soup.find('tbody')
        return [AtCoderProblem._from_table_row(tr) for tr in tbody.find_all('tr')]


class AtCoderProblem(onlinejudge.type.Problem):
    """
    :ivar contest_id: :py:class:`str`
    :ivar problem_id: :py:class:`str`

    :note: AtCoder has problems independently from contests. Therefore the notions `contest_id`, `alphabet`, and `url` don't belong to problems itself.
    """

    def __init__(self, contest_id: str, problem_id: str):
        self.contest_id = contest_id
        self.problem_id = problem_id  # TODO: fix the name, since AtCoder calls this as "task_screen_name"
        self._task_id = None  # type: Optional[int]
        self._task_name = None  # type: Optional[str]
        self._time_limit_msec = None  # type: Optional[int]
        self._memory_limit_byte = None  # type: Optional[int]
        self._alphabet = None  # type: Optional[str]

    @classmethod
    def _from_table_row(cls, tr: bs4.Tag) -> 'AtCoderProblem':
        tds = tr.find_all('td')
        assert len(tds) == 5
        path = tds[1].find('a')['href']
        self = cls.from_url('https://atcoder.jp' + path)
        assert self is not None
        self._alphabet = tds[0].text
        self._task_name = tds[1].text
        self._time_limit_msec = int(float(utils.remove_suffix(tds[2].text, ' sec')) * 1000)
        self._memory_limit_byte = int(utils.remove_suffix(tds[3].text, ' MB')) * 1000 * 1000  # TODO: confirm this is MB truly, not MiB
        assert tds[4].text.strip() in ('', 'Submit')
        return self

    def download_sample_cases(self, session: Optional[requests.Session] = None) -> List[onlinejudge.type.TestCase]:
        session = session or utils.new_default_session()
        # get
        resp = _request('GET', self.get_url(), session=session)
        msgs = AtCoderService._get_messages_from_cookie(resp.cookies)
        if AtCoderService._report_messages(msgs, unexpected=True):
            # example message: "message: You cannot see this page."
            log.warning('are you logged in?')
            return []
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        samples = utils.SampleZipper()
        lang = None
        for pre, h3 in self._find_sample_tags(soup):
            s = utils.textfile(utils.dos2unix(pre.string.lstrip()))
            name = h3.string
            l = self._get_tag_lang(pre)
            if lang is None:
                lang = l
            elif lang != l:
                log.info('skipped due to language: current one is %s, not %s: %s ', lang, l, name)
                continue
            samples.add(s, name)
        return samples.get()

    def _get_tag_lang(self, tag):
        assert isinstance(tag, bs4.Tag)
        for parent in tag.parents:
            for cls in parent.attrs.get('class') or []:
                if cls.startswith('lang-'):
                    return cls

    def _find_sample_tags(self, soup) -> Generator[Tuple[bs4.Tag, bs4.Tag], None, None]:
        for pre in soup.find_all('pre'):
            log.debug('pre tag: %s', str(pre))
            if not pre.string:
                continue
            prv = utils.previous_sibling_tag(pre)

            # the first format: h3+pre
            if prv and prv.name == 'h3' and prv.string:
                yield (pre, prv)

            else:
                # ignore tags which are not samples
                # example: https://atcoder.jp/contests/abc003/tasks/abc003_4
                while prv is not None:
                    if prv.name == 'pre':
                        break
                    prv = utils.previous_sibling_tag(prv)
                if prv is not None:
                    continue

                # the second format: h3+section pre
                if pre.parent and pre.parent.name == 'section':
                    prv = pre.parent and utils.previous_sibling_tag(pre.parent)
                    if prv and prv.name == 'h3' and prv.string:
                        yield (pre, prv)

    def get_url(self) -> str:
        return 'http://{}.contest.atcoder.jp/tasks/{}'.format(self.contest_id, self.problem_id)

    def get_service(self) -> AtCoderService:
        return AtCoderService()

    def get_contest(self) -> AtCoderContest:
        return AtCoderContest(self.contest_id)

    @classmethod
    def from_url(cls, s: str) -> Optional['AtCoderProblem']:
        # example: http://agc012.contest.atcoder.jp/tasks/agc012_d
        result = urllib.parse.urlparse(s)
        dirname, basename = posixpath.split(utils.normpath(result.path))
        if result.scheme in ('', 'http', 'https') \
                and result.netloc.count('.') == 3 \
                and result.netloc.endswith('.contest.atcoder.jp') \
                and result.netloc.split('.')[0] \
                and dirname == '/tasks' \
                and basename:
            contest_id = result.netloc.split('.')[0]
            problem_id = basename
            return cls(contest_id, problem_id)

        # example: https://beta.atcoder.jp/contests/abc073/tasks/abc073_a
        m = re.match(r'^/contests/([\w\-_]+)/tasks/([\w\-_]+)$', utils.normpath(result.path))
        if result.scheme in ('', 'http', 'https') \
                and result.netloc in ('atcoder.jp', 'beta.atcoder.jp') \
                and m:
            contest_id = m.group(1)
            problem_id = m.group(2)
            return cls(contest_id, problem_id)

        return None

    def get_input_format(self, session: Optional[requests.Session] = None) -> str:
        session = session or utils.new_default_session()
        # get
        resp = _request('GET', self.get_url(), session=session)
        msgs = AtCoderService._get_messages_from_cookie(resp.cookies)
        if AtCoderService._report_messages(msgs, unexpected=True):
            return ''
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        for h3 in soup.find_all('h3'):
            if h3.string in ('入力', 'Input'):
                tag = h3
                for _ in range(3):
                    tag = utils.next_sibling_tag(tag)
                    if tag is None:
                        break
                    if tag.name in ('pre', 'blockquote'):
                        s = ''
                        for it in tag:
                            s += it.string or it  # AtCoder uses <var>...</var> for math symbols
                        return s
        return ''

    def get_language_dict(self, session: Optional[requests.Session] = None) -> Dict[str, onlinejudge.type.Language]:
        session = session or utils.new_default_session()
        # get
        url = 'http://{}.contest.atcoder.jp/submit'.format(self.contest_id)
        resp = _request('GET', url, session=session)
        msgs = AtCoderService._get_messages_from_cookie(resp.cookies)
        if AtCoderService._report_messages(msgs, unexpected=True):
            return {}
        # check whether logged in
        path = utils.normpath(urllib.parse.urlparse(resp.url).path)
        if path.startswith('/login'):
            log.error('not logged in')
            return {}
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        select = soup.find('select', class_='submit-language-selector')  # NOTE: AtCoder can vary languages depending on tasks, even in one contest. here, ignores this fact.
        language_dict = {}
        for option in select.find_all('option'):
            language_dict[option.attrs['value']] = {'description': option.string}
        return language_dict

    def submit_code(self, code: bytes, language: str, session: Optional[requests.Session] = None) -> onlinejudge.type.DummySubmission:
        assert language in self.get_language_dict(session=session)
        session = session or utils.new_default_session()
        # get
        url = 'http://{}.contest.atcoder.jp/submit'.format(self.contest_id)  # TODO: use beta.atcoder.jp
        resp = _request('GET', url, session=session)
        msgs = AtCoderService._get_messages_from_cookie(resp.cookies)
        if AtCoderService._report_messages(msgs, unexpected=True):
            raise SubmissionError
        # check whether logged in
        path = utils.normpath(urllib.parse.urlparse(resp.url).path)
        if path.startswith('/login'):
            log.error('not logged in')
            raise SubmissionError
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        form = soup.find('form', action=re.compile(r'^/submit\?task_id='))
        if not form:
            log.error('form not found')
            raise SubmissionError
        log.debug('form: %s', str(form))
        # post
        task_id = self._get_task_id(session=session)
        form = utils.FormSender(form, url=resp.url)
        form.set('task_id', str(task_id))
        form.set('source_code', code)
        form.set('language_id_{}'.format(task_id), language)
        resp = form.request(session=session)
        resp.raise_for_status()
        # result
        msgs = AtCoderService._get_messages_from_cookie(resp.cookies)
        AtCoderService._report_messages(msgs)
        if '/submissions/me' in resp.url:
            # example: https://practice.contest.atcoder.jp/submissions/me#32174
            # CAUTION: this URL is not a URL of the submission
            log.success('success: result: %s', resp.url)
            # NOTE: ignore the returned legacy URL and use beta.atcoder.jp's one
            url = 'https://beta.atcoder.jp/contests/{}/submissions/me'.format(self.contest_id)
            return onlinejudge.type.DummySubmission(url)
        else:
            log.failure('failure')
            log.debug('redirected to %s', resp.url)
            raise SubmissionError

    def _get_task_id(self, session: Optional[requests.Session] = None) -> int:
        if self._task_id is None:
            session = session or utils.new_default_session()
            # get
            resp = _request('GET', self.get_url(), session=session)
            msgs = AtCoderService._get_messages_from_cookie(resp.cookies)
            if AtCoderService._report_messages(msgs, unexpected=True):
                raise SubmissionError
            # parse
            soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
            submit = soup.find('a', href=re.compile(r'^/submit\?task_id='))
            if not submit:
                log.error('link to submit not found')
                raise SubmissionError
            m = re.match(r'^/submit\?task_id=([0-9]+)$', submit.attrs['href'])
            assert m
            self._task_id = int(m.group(1))
        return self._task_id

    def _load_details(self, session: Optional[requests.Session] = None) -> int:
        raise NotImplementedError

    get_task_name = utils.getter_with_load_details('_task_name')  # type: Callable[..., str]
    get_time_limit_msec = utils.getter_with_load_details('_time_limit_msec')  # type: Callable[..., int]
    get_memory_limit_byte = utils.getter_with_load_details('_memory_limit_byte')  # type: Callable[..., int]
    get_alphabet = utils.getter_with_load_details('_alphabet')  # type: Callable[..., str]


class AtCoderSubmission(onlinejudge.type.Submission):
    """
    :ivar contest_id: :py:class:`str`
    :ivar submission_id: :py:class:`str`
    """

    def __init__(self, contest_id: str, submission_id: int, problem_id: Optional[str] = None):
        self.contest_id = contest_id
        self.submission_id = submission_id
        self._problem_id = problem_id
        self._source_code = None  # type: Optional[bytes]
        self._submission_time = None  # type: Optional[datetime.datetime]
        self._user_id = None  # type: Optional[str]
        self._language_name = None  # type: Optional[str]
        self._score = None  # type: Optional[int]
        self._code_size = None  # type: Optional[int]
        self._status = None  # type: Optional[str]
        self._exec_time_msec = None  # type: Optional[int]
        self._memory_byte = None  # type: Optional[int]
        self._compile_error = None  # type: Optional[str]
        self._test_sets = None  # type: Optional[List[AtCoderSubmissionTestSet]]
        self._test_cases = None  # type: Optional[List[AtCoderSubmissionTestCaseResult]]

    @classmethod
    def from_url(cls, s: str, problem_id: Optional[str] = None) -> Optional['AtCoderSubmission']:
        submission_id = None  # type: Optional[int]

        # example: http://agc001.contest.atcoder.jp/submissions/1246803
        result = urllib.parse.urlparse(s)
        dirname, basename = posixpath.split(utils.normpath(result.path))
        if result.scheme in ('', 'http', 'https') \
                and result.netloc.count('.') == 3 \
                and result.netloc.endswith('.contest.atcoder.jp') \
                and result.netloc.split('.')[0] \
                and dirname == '/submissions':
            contest_id = result.netloc.split('.')[0]
            try:
                submission_id = int(basename)
            except ValueError:
                pass
                submission_id = None
            if submission_id is not None:
                return cls(contest_id, submission_id, problem_id=problem_id)

        # example: https://beta.atcoder.jp/contests/abc073/submissions/1592381
        m = re.match(r'^/contests/([\w\-_]+)/submissions/(\d+)$', utils.normpath(result.path))
        if result.scheme in ('', 'http', 'https') \
                and result.netloc in ('atcoder.jp', 'beta.atcoder.jp') \
                and m:
            contest_id = m.group(1)
            try:
                submission_id = int(m.group(2))
            except ValueError:
                submission_id = None
            if submission_id is not None:
                return cls(contest_id, submission_id, problem_id=problem_id)

        return None

    def get_url(self, type: str = 'latest', lang: Optional[str] = None) -> str:
        if type == 'latest' or type == 'beta':
            url = 'https://atcoder.jp/contests/{}/submissions/{}'.format(self.contest_id, self.submission_id)
        elif type == 'old':
            url = 'https://{}.contest.atcoder.jp/submissions/{}'.format(self.contest_id, self.submission_id)
        else:
            assert False
        if lang is not None:
            url += '?lang={}'.format(lang)
        return url

    def get_service(self) -> AtCoderService:
        return AtCoderService()

    def download(self, session: Optional[requests.Session] = None) -> str:
        return self.get_source_code(session=session).decode()

    def _load_details(self, session: Optional[requests.Session] = None) -> None:
        session = session or utils.new_default_session()
        resp = _request('GET', self.get_url(type='beta', lang='en'), session=session)
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)

        # Submission #N
        id_, = soup.find_all('span', class_='h2')
        assert id_.text == 'Submission #{}'.format(self.submission_id)

        # Source Code
        source_code = soup.find(id='submission-code')
        self._source_code = source_code.text.encode()

        submission_info, test_cases_summary, test_cases_data = soup.find_all('table')

        # Submission Info
        data = {}  # type: Dict[str, str]
        for tr in submission_info.find_all('tr'):
            key = tr.find('th').text.strip()
            value = tr.find('td').text.strip()
            data[key] = value

            if key == 'Task':
                problem = AtCoderProblem.from_url('https://atcoder.jp' + tr.find('a')['href'])
                assert problem is not None
                self._problem_id = problem.problem_id

        self._submission_time = datetime.datetime.strptime(data['Submission Time'], '%Y-%m-%d %H:%M:%S+0900').replace(tzinfo=utils.tzinfo_jst)
        self._user_id = data['User']
        self._language_name = data['Language']
        self._score = int(data['Score'])
        self._code_size = int(utils.remove_suffix(data['Code Size'], ' Byte'))
        self._status = data['Status']
        if 'Exec Time' in data:
            self._exec_time_msec = int(utils.remove_suffix(data['Exec Time'], ' ms'))
        if 'Memory' in data:
            self._memory_byte = int(utils.remove_suffix(data['Memory'], ' KB')) * 1000  # TODO: confirm this is KB truly, not KiB

        # Compile Error
        compile_error = soup.find('h4', text='Compile Error')
        if compile_error is None:
            self.compile_error = ''
        else:
            compile_error = compile_error.find_next_sibling('pre')
            self.compile_error = compile_error.text

        # Test Cases
        trs = test_cases_summary.find('tbody').find_all('tr')
        self._test_sets = [AtCoderSubmissionTestSet._from_table_row(tr) for tr in trs]
        trs = test_cases_data.find('tbody').find_all('tr')
        self._test_cases = [AtCoderSubmissionTestCaseResult._from_table_row(tr) for tr in trs]

    def get_problem(self, session: Optional[requests.Session] = None) -> AtCoderProblem:
        if self._problem_id is None:
            self._load_details(session=session)
        assert self._problem_id is not None
        return AtCoderProblem(self.contest_id, self._problem_id)

    get_source_code = utils.getter_with_load_details('_source_code')  # type: Callable[..., bytes]
    get_compile_error = utils.getter_with_load_details('_compiler_error')  # type: Callable[..., str]
    get_user_id = utils.getter_with_load_details('_user_id')  # type: Callable[..., str]
    get_submission_time = utils.getter_with_load_details('_submission_time')  # type: Callable[..., datetime.datetime]
    get_language_name = utils.getter_with_load_details('_language_name')  # type: Callable[..., str]
    get_score = utils.getter_with_load_details('_score')  # type: Callable[..., int]
    get_code_size = utils.getter_with_load_details('_code_size')  # type: Callable[..., int]
    get_status = utils.getter_with_load_details('_status')  # type: Callable[..., str]
    get_exec_time_msec = utils.getter_with_load_details('_exec_time_msec', check_with='_status')  # type: Callable[..., int]
    get_memory_byte = utils.getter_with_load_details('_memory_byte', check_with='_status')  # type: Callable[..., int]
    get_test_sets = utils.getter_with_load_details('_test_sets')  # type: Callable[..., List[AtCoderSubmissionTestSet]]
    get_test_cases = utils.getter_with_load_details('_test_cases')  # type: Callable[..., List[AtCoderSubmissionTestCaseResult]]


class AtCoderSubmissionTestSet(object):
    """
    :ivar set_name: :py:class:`str`
    :ivar score: :py:class:`int`
    :ivar max_score: :py:class:`int`
    :ivar test_case_names: :py:class:`List` [ :py:class:`str` ]
    """

    def __init__(self, set_name: str, score: int, max_score: int, test_case_names: List[str]):
        self.set_name = set_name
        self.score = score
        self.max_score = max_score
        self.test_case_names = test_case_names

    @classmethod
    def _from_table_row(cls, tr: bs4.Tag) -> 'AtCoderSubmissionTestSet':
        tds = tr.find_all('td')
        assert len(tds) == 3
        set_name = tds[0].text
        score, max_score = [int(s) for s in tds[1].text.split('/')]
        test_case_names = tds[2].text.split(', ')
        return AtCoderSubmissionTestSet(set_name, score, max_score, test_case_names)


class AtCoderSubmissionTestCaseResult(object):
    """
    :ivar case_name: :py:class:`str`
    :ivar status: :py:class:`str`
    :ivar exec_time_msec: :py:class:`int` in millisecond
    :ivar memory_byte: :py:class:`int` in byte
    """

    def __init__(self, case_name: str, status: str, exec_time_msec: Optional[int], memory_byte: Optional[int]):
        self.case_name = case_name
        self.status = status
        self.exec_time_msec = exec_time_msec
        self.memory_byte = memory_byte

    @classmethod
    def _from_table_row(cls, tr: bs4.Tag) -> 'AtCoderSubmissionTestCaseResult':
        tds = tr.find_all('td')
        case_name = tds[0].text
        status = tds[1].text
        exec_time_msec = None  # type: Optional[int]
        memory_byte = None  # type: Optional[int]
        if len(tds) == 4:
            exec_time_msec = int(utils.remove_suffix(tds[2].text, ' ms'))
            memory_byte = int(utils.remove_suffix(tds[3].text, ' KB')) * 1000  # TODO: confirm this is KB truly, not KiB
        else:
            assert len(tds) == 2
        return AtCoderSubmissionTestCaseResult(case_name, status, exec_time_msec, memory_byte)


onlinejudge.dispatch.services += [AtCoderService]
onlinejudge.dispatch.problems += [AtCoderProblem]
onlinejudge.dispatch.submissions += [AtCoderSubmission]
