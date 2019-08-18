# Python Version: 3.x
# -*- coding: utf-8 -*-
"""
the module for AtCoder (https://atcoder.jp/)

:note: There are some useful endpoints:

    -   https://atcoder.jp/contests/abc001/standings/json
    -   https://atcoder.jp/users/chokudai/history/json

:note: There is an unofficial API https://github.com/kenkoooo/AtCoderProblems

:note: Some methods not inherited from classes :py:mod:`onlinejudge.type` may be modified in future, because the specification is not fixed yet.
"""

import datetime
import itertools
import posixpath
import re
import urllib.parse
from typing import *

import bs4

import onlinejudge._implementation.logging as log
import onlinejudge._implementation.testcase_zipper
import onlinejudge._implementation.utils as utils
import onlinejudge.dispatch
import onlinejudge.type
from onlinejudge.type import *


def _list_alert(resp: requests.Response, soup: Optional[bs4.BeautifulSoup] = None, print_: bool = False) -> List[str]:
    if soup is None:
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
    msgs = []  # type: List[str]
    for alert in soup.find_all('div', attrs={'role': 'alert'}):
        msg = ' '.join([s.strip() for s in alert.strings if s.strip()])
        if print_:
            log.warning('AtCoder says: %s', msg)
        msgs += [msg]
    return msgs


def _request(*args, **kwargs):
    """
    This is a workaround. AtCoder's servers sometime fail to send "Content-Type" field.
    see https://github.com/kmyk/online-judge-tools/issues/28 and https://github.com/kmyk/online-judge-tools/issues/232
    """
    resp = utils.request(*args, **kwargs)
    log.debug('AtCoder\'s server said "Content-Type: %s"', resp.headers.get('Content-Type', '(not sent)'))
    resp.encoding = 'UTF-8'
    _list_alert(resp, print_=True)
    return resp


class AtCoderService(onlinejudge.type.Service):
    def login(self, *, get_credentials: onlinejudge.type.CredentialsProvider, session: Optional[requests.Session] = None) -> None:
        """
        :raises LoginError:
        """

        session = session or utils.get_default_session()
        if self.is_logged_in(session=session):
            return

        # get
        url = 'https://atcoder.jp/login'
        resp = _request('GET', url, session=session, allow_redirects=False)

        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        form = soup.find('form', action='')
        if not form:
            raise LoginError('something wrong')

        # post
        username, password = get_credentials()
        form = utils.FormSender(form, url=resp.url)
        form.set('username', username)
        form.set('password', password)
        resp = form.request(session)
        _list_alert(resp, print_=True)

        # result
        if 'login' not in resp.url:
            log.success('Welcome,')  # AtCoder redirects to the top page if success
        else:
            log.failure('Username or Password is incorrect.')
            raise LoginError

    def is_logged_in(self, *, session: Optional[requests.Session] = None) -> bool:
        session = session or utils.get_default_session()
        url = 'https://atcoder.jp/contests/practice/submit'
        resp = _request('GET', url, session=session, allow_redirects=False)
        return resp.status_code == 200

    def get_url(self) -> str:
        return 'https://atcoder.jp/'

    def get_name(self) -> str:
        return 'AtCoder'

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

    def iterate_contest_contents(self, *, lang: str = 'ja', session: Optional[requests.Session] = None) -> Iterator['AtCoderContestContentPartial']:
        """
        :param lang: must be `ja` (default) or `en`.
        :note: `lang=ja` is required to see some Japanese-local contests.
        :note: You can use `lang=en` to see the English names of contests.
        """

        assert lang in ('ja', 'en')
        session = session or utils.get_default_session()
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

    def iterate_contests(self, *, lang: str = 'ja', session: Optional[requests.Session] = None) -> Iterator['AtCoderContest']:
        for content in self.iterate_contest_contents(lang=lang, session=session):
            yield content.contest

    def get_user_history_url(self, user_id: str) -> str:
        return 'https://atcoder.jp/users/{}/history/json'.format(user_id)


# TODO: use the new style of NamedTuple added from Pyhon 3.6
AtCoderContestContentPartial = NamedTuple('AtCoderContestContentPartial', [
    ('tag', bs4.Tag),
    ('contest', 'AtCoderContest'),
    ('lang', str),
    ('start_time', datetime.datetime),
    ('name', str),
    ('duration', datetime.timedelta),
    ('rated_range', str),
])

# TODO: use the new style of NamedTuple added from Pyhon 3.6
AtCoderContestContent = NamedTuple('AtCoderContestContent', [
    ('session', requests.Session),
    ('response', requests.Response),
    ('contest', 'AtCoderContest'),
    ('lang', str),
    ('start_time', datetime.datetime),
    ('name', str),
    ('duration', datetime.timedelta),
    ('rated_range', str),
    ('can_participate', str),
    ('penalty', datetime.timedelta),
])


class AtCoderContest(onlinejudge.type.Contest):
    """
    :ivar contest_id: :py:class:`str`
    """
    def __init__(self, *, contest_id: str):
        if contest_id.startswith('http'):
            # an exception should be raised since mypy cannot check this kind of failure
            raise ValueError('You should use AtCoderContest.from_url(url) instead of AtCoderContest(url)')
        self.contest_id = contest_id

    def get_url(self, *, type: Optional[str] = None, lang: Optional[str] = None) -> str:
        if type is None or type == 'beta':
            url = 'https://atcoder.jp/contests/{}'.format(self.contest_id)
        elif type == 'old':
            url = 'http://{}.contest.atcoder.jp/'.format(self.contest_id)
        else:
            assert False
        if lang is not None:
            url += '?lang={}'.format(lang)
        return url

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
            return cls(contest_id=contest_id)

        # example: https://atcoder.jp/contests/agc030
        if result.scheme in ('', 'http', 'https') and result.hostname in ('atcoder.jp', 'beta.atcoder.jp'):
            m = re.match(r'/contests/([\w\-_]+)/?.*', utils.normpath(result.path))
            if m:
                contest_id = m.group(1)
                return cls(contest_id=contest_id)

        return None

    @classmethod
    def _from_table_row(cls, tr: bs4.Tag, *, lang: str) -> AtCoderContestContentPartial:
        tds = tr.find_all('td')
        assert len(tds) == 4
        anchors = [tds[0].find('a'), tds[1].find('a')]
        contest_path = anchors[1]['href']
        assert contest_path.startswith('/contests/')
        contest_id = contest_path[len('/contests/'):]
        self = AtCoderContest(contest_id=contest_id)
        name = anchors[1].text
        start_time = self._parse_start_time(anchors[0]['href'])
        hours, minutes = map(int, tds[2].text.split(':'))
        duration = datetime.timedelta(hours=hours, minutes=minutes)
        rated_range = tds[3].text
        return AtCoderContestContentPartial(
            tag=tr,
            contest=self,
            lang=lang,
            name=name,
            start_time=start_time,
            duration=duration,
            rated_range=rated_range,
        )

    def _parse_start_time(self, url: str) -> datetime.datetime:
        # TODO: we need to use an ISO-format parser
        query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        assert len(query['iso']) == 1
        assert query['p1'] == ['248']  # means JST
        return datetime.datetime.strptime(query['iso'][0], '%Y%m%dT%H%M').replace(tzinfo=utils.tzinfo_jst)

    def download_content(self, *, session: Optional[requests.Session] = None, lang: str = 'en') -> AtCoderContestContent:
        assert lang in ('en', 'ja')
        session = session or utils.get_default_session()
        resp = _request('GET', self.get_url(type='beta', lang=lang), session=session)
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)

        name, _, _ = soup.find('title').text.rpartition(' - ')
        contest_duration = soup.find('small', class_='contest-duration')
        start_time, end_time = [self._parse_start_time(a['href']) for a in contest_duration.find_all('a')]
        duration = end_time - start_time
        _, _, can_participate = soup.find('span', text=re.compile(r'^(Can Participate|参加対象): ')).text.partition(': ')
        _, _, rated_range = soup.find('span', text=re.compile(r'^(Rated Range|Rated対象): ')).text.partition(': ')

        penalty_text = soup.find('span', text=re.compile(r'^(Penalty|ペナルティ): ')).text
        if lang == 'en' and penalty_text == 'Penalty: None':
            minutes = 0
        elif lang == 'ja' and penalty_text == 'ペナルティ: なし':
            minutes = 0
        else:
            m = re.match(r'(Penalty|ペナルティ): (\d+)( minutes?|分)', penalty_text)
            assert m
            minutes = int(m.group(2))
        penalty = datetime.timedelta(minutes=minutes)

        return AtCoderContestContent(
            session=session,
            response=resp,
            contest=self,
            lang=lang,
            start_time=start_time,
            name=name,
            duration=duration,
            rated_range=rated_range,
            can_participate=can_participate,
            penalty=penalty,
        )

    def get_service(self) -> AtCoderService:
        return AtCoderService()

    def list_problem_contents(self, *, session: Optional[requests.Session] = None) -> List['AtCoderProblemContentPartial']:
        # get
        session = session or utils.get_default_session()
        url = 'https://atcoder.jp/contests/{}/tasks'.format(self.contest_id)
        resp = _request('GET', url, session=session)

        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        tbody = soup.find('tbody')
        return [AtCoderProblem._from_table_row(tr) for tr in tbody.find_all('tr')]

    # TODO: why does this require "type: ignore"?
    def list_problems(self, *, session: Optional[requests.Session] = None) -> 'List[AtCoderProblem]':  # type: ignore
        return [content.problem for content in self.list_problem_contents(session=session)]

    def iterate_submission_contents_where(
            self,
            *,
            me: bool = False,
            problem_id: Optional[str] = None,
            language_id: Optional[LanguageId] = None,
            status: Optional[str] = None,
            user_glob: Optional[str] = None,
            order: Optional[str] = None,
            desc: bool = False,
            lang: Optional[str] = None,
            pages: Optional[Iterator[int]] = None,
            session: Optional[requests.Session] = None,
    ) -> Iterator['AtCoderSubmissionContentPartial']:
        """
        :note: If you use certain combination of options, then the results may not correct when there are new submissions while crawling.
        :param status: must be one of `AC`, `WA`, `TLE`, `MLE`, `RE`, `CLE`, `OLE`, `IE`, `WJ`, `WR`, or `Judging`
        :param order: must be one of `created`, `score`, `source_length`, `time_consumption`, or `memory_consumption`
        :param me: use the `.../submissions/me` page instead of `.../submission`
        :param user_glob: is used as the value of `f.User` query parameter
        :param language_id: is used as the value of `f.Language` query parameter
        :param lang: must be one of `ja`, `en`
        :param pages: is an iterator to list the page numbers to GET
        """
        assert status in (None, 'AC', 'WA', 'TLE', 'MLE', 'RE', 'CE', 'QLE', 'OLE', 'IE', 'WJ', 'WR', 'Judging')
        assert order in (None, 'created', 'score', 'source_length', 'time_consumption', 'memory_consumption')
        if desc:
            assert order is not None

        base_url = 'https://atcoder.jp/contests/{}/submissions'.format(self.contest_id)
        if me:
            base_url += '/me'
        params = {}
        if problem_id is not None:
            params['f.Task'] = problem_id
        if language_id is not None:
            params['f.Language'] = language_id
        if status is not None:
            params['f.Status'] = status
        if user_glob is not None:
            params['f.User'] = user_glob
        if order is not None:
            params['orderBy'] = order
        if desc:
            params['desc'] = 'true'

        # get
        session = session or utils.get_default_session()
        for page in pages or itertools.count(1):
            params_page = ({'page': str(page)} if page >= 2 else {})
            url = base_url + '?' + urllib.parse.urlencode({**params, **params_page})
            resp = _request('GET', url, session=session)

            submissions = list(self._iterate_submission_contents_from_response(resp=resp))
            if not submissions:
                break
            yield from submissions

    def _iterate_submission_contents_from_response(self, *, resp: requests.Response) -> Iterator['AtCoderSubmissionContentPartial']:
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        tbodies = soup.find_all('tbody')
        if len(tbodies) == 0:
            return  # No Submissions
        assert len(tbodies) == 1
        tbody = tbodies[0]
        for tr in tbody.find_all('tr'):
            yield AtCoderSubmission._from_table_row(tr, contest_id=self.contest_id)

    def iterate_submissions_where(self, **kwargs) -> Iterator['AtCoderSubmission']:
        for content in self.iterate_submission_contents_where(**kwargs):
            yield content.submission

    def iterate_submissions(self, *, session: Optional[requests.Session] = None) -> Iterator['AtCoderSubmission']:
        """
        :note: in implementation, use "ORDER BY created DESC" to list all submissions even when there are new submissions
        """
        yield from self.iterate_submissions_where(order='created', desc=False, session=session)


# TODO: use the new style of NamedTuple added from Pyhon 3.6
AtCoderProblemContentPartial = NamedTuple('AtCoderProblemContentPartial', [
    ('tag', bs4.Tag),
    ('alphabet', str),
    ('memory_limit_byte', int),
    ('name', str),
    ('problem', 'AtCoderProblem'),
    ('time_limit_msec', int),
])


def _AtCoderProblemContentPartial_from_row(tr: bs4.Tag):
    tds = tr.find_all('td')
    assert 4 <= len(tds) <= 5
    path = tds[1].find('a')['href']
    problem = AtCoderProblem.from_url('https://atcoder.jp' + path)
    assert problem is not None
    alphabet = tds[0].text
    name = tds[1].text
    if tds[2].text.endswith(' msec'):
        time_limit_msec = int(utils.remove_suffix(tds[2].text, ' msec'))
    elif tds[2].text.endswith(' sec'):
        time_limit_msec = int(float(utils.remove_suffix(tds[2].text, ' sec')) * 1000)
    else:
        assert False
    if tds[3].text.endswith(' KB'):
        memory_limit_byte = int(float(utils.remove_suffix(tds[3].text, ' KB')) * 1000)
    elif tds[3].text.endswith(' MB'):
        memory_limit_byte = int(float(utils.remove_suffix(tds[3].text, ' MB')) * 1000 * 1000)  # TODO: confirm this is MB truly, not MiB
    else:
        assert False
    if len(tds) == 5:
        assert tds[4].text.strip() in ('', 'Submit', '提出')

    return AtCoderProblemContentPartial(
        tag=tr,
        alphabet=alphabet,
        memory_limit_byte=memory_limit_byte,
        name=name,
        problem=problem,
        time_limit_msec=time_limit_msec,
    )


# TODO: use the new style of NamedTuple added from Pyhon 3.6
AtCoderProblemContent = NamedTuple('AtCoderProblemContent', [
    ('session', Optional[requests.Session]),
    ('response', Optional[requests.Response]),
    ('alphabet', str),
    ('available_languages', Optional[List[Language]]),
    ('html', str),
    ('input_format', Optional[str]),
    ('memory_limit_byte', int),
    ('name', str),
    ('problem', 'AtCoderProblem'),
    ('sample_cases', List[TestCase]),
    ('score', Optional[int]),
    ('time_limit_msec', int),
])


def _AtCoderProblemContent_get_tag_lang(tag: bs4.Tag):
    assert isinstance(tag, bs4.Tag)
    for parent in tag.parents:
        for cls in parent.attrs.get('class') or []:
            if cls.startswith('lang-'):
                return cls


def _AtCoderProblemContent_find_sample_tags(soup: bs4.BeautifulSoup) -> Iterator[Tuple[bs4.Tag, bs4.Tag]]:
    for pre in soup.find_all('pre'):
        log.debug('pre tag: %s', str(pre))
        if not pre.string:
            continue

        def h3_plus(tag):
            prv = tag.find_previous_sibling()
            if prv and prv.name == 'h3' and prv.string:
                yield (pre, prv)

        # the first format: h3+pre
        yield from h3_plus(pre)

        # the second format: h3+section pre
        if pre.parent and pre.parent.name == 'section':
            # ignore tags which are not samples
            # example: https://atcoder.jp/contests/abc003/tasks/abc003_4
            if pre.find_previous_sibling('pre') is None:
                yield from h3_plus(pre.parent)


def _AtCoderProblemContent_parse_sample_cases(soup: bs4.BeautifulSoup) -> List[onlinejudge.type.TestCase]:
    samples = onlinejudge._implementation.testcase_zipper.SampleZipper()
    lang = None
    for pre, h3 in _AtCoderProblemContent_find_sample_tags(soup):
        s = utils.textfile(utils.dos2unix(pre.string.lstrip()))
        name = h3.string
        l = _AtCoderProblemContent_get_tag_lang(pre)
        if lang is None:
            lang = l
        elif lang != l:
            log.info('skipped due to language: current one is %s, not %s: %s ', lang, l, name)
            continue
        samples.add(s.encode(), name)
    return samples.get()


def _AtCoderProblemContent_parse_input_format(soup: bs4.BeautifulSoup) -> Optional[str]:
    for h3 in soup.find_all('h3', text=re.compile(r'^(入力|Input)$')):
        if h3.parent.name == 'section':
            section = h3.parent
        else:
            section = h3.find_next_sibling('section')
        if section is None:
            section = soup.find(class_='io-style')
        if section is None:
            log.warning('<section> tag not found. something wrong')
            return None
        pre = section.find('pre')
        if pre is not None:
            return pre.decode_contents(formatter=None)
    return None


def _AtCoderProblemContent_parse_available_languages(soup: bs4.BeautifulSoup, problem: 'AtCoderProblem') -> Optional[List[Language]]:
    form = soup.find('form', action='/contests/{}/submit'.format(problem.contest_id))
    if form is None:
        return None
    select = form.find('div', id='select-lang').find('select', attrs={'name': 'data.LanguageId'})  # NOTE: AtCoder can vary languages depending on tasks, even in one contest. here, ignores this fact.
    languages = []  # type: List[Language]
    for option in select.find_all('option'):
        languages += [Language(option.attrs['value'], option.string)]
    return languages


def _AtCoderProblemContent_parse_partial(soup: bs4.BeautifulSoup, problem: 'AtCoderProblem') -> AtCoderProblemContentPartial:
    h2 = soup.find('span', class_='h2')

    alphabet, _, name = h2.text.partition(' - ')

    time_limit, memory_limit = h2.find_next_sibling('p').text.split(' / ')
    for time_limit_prefix in ('実行時間制限: ', 'Time Limit: '):
        if time_limit.startswith(time_limit_prefix):
            break
    else:
        assert False
    if time_limit.endswith(' msec'):
        time_limit_msec = int(utils.remove_suffix(utils.remove_prefix(time_limit, time_limit_prefix), ' msec'))
    elif time_limit.endswith(' sec'):
        time_limit_msec = int(float(utils.remove_suffix(utils.remove_prefix(time_limit, time_limit_prefix), ' sec')) * 1000)
    else:
        assert False

    for memory_limit_prefix in ('メモリ制限: ', 'Memory Limit: '):
        if memory_limit.startswith(memory_limit_prefix):
            break
    else:
        assert False
    if memory_limit.endswith(' KB'):
        memory_limit_byte = int(float(utils.remove_suffix(utils.remove_prefix(memory_limit, memory_limit_prefix), ' KB')) * 1000)
    elif memory_limit.endswith(' MB'):
        memory_limit_byte = int(float(utils.remove_suffix(utils.remove_prefix(memory_limit, memory_limit_prefix), ' MB')) * 1000 * 1000)
    else:
        assert False

    return AtCoderProblemContentPartial(
        alphabet=alphabet,
        memory_limit_byte=memory_limit_byte,
        name=name,
        problem=problem,
        tag=soup,
        time_limit_msec=time_limit_msec,
    )


def _AtCoderProblemContent_parse_score(soup: bs4.BeautifulSoup) -> Optional[int]:
    task_statement = soup.find('div', id='task-statement')
    p = task_statement.find('p')  # first
    if p is not None and p.text.startswith('配点 : '):
        score = utils.remove_suffix(utils.remove_prefix(p.text, '配点 : '), ' 点')
        try:
            return int(score)
        except ValueError:
            # some problems have scores like "<p>配点 : \(100\) 点</p>", not "<p>配点 : 100 点</p>"
            # example: https://atcoder.jp/contests/wupc2019/tasks/wupc2019_a
            pass
    return None


def _AtCoderProblemContent_from_html(html: str, *, problem: 'AtCoderProblem', session: Optional[requests.Session] = None, response: Optional[requests.Response] = None) -> AtCoderProblemContent:
    """
    :param html: must be a HTML of the new (beta) version of AtCoder

    .. versionadded:: 6.2.0

    """

    soup = bs4.BeautifulSoup(html, utils.html_parser)
    sample_cases = _AtCoderProblemContent_parse_sample_cases(soup)
    input_format = _AtCoderProblemContent_parse_input_format(soup)
    available_languages = _AtCoderProblemContent_parse_available_languages(soup, problem=problem)
    partial = _AtCoderProblemContent_parse_partial(soup, problem=problem)
    score = _AtCoderProblemContent_parse_score(soup)
    return AtCoderProblemContent(
        session=session,
        response=response,
        alphabet=partial.alphabet,
        available_languages=available_languages,
        html=html,
        input_format=input_format,
        memory_limit_byte=partial.memory_limit_byte,
        name=partial.name,
        problem=problem,
        sample_cases=sample_cases,
        score=score,
        time_limit_msec=partial.time_limit_msec,
    )


AtCoderProblemContent.from_html = _AtCoderProblemContent_from_html  # type: ignore


class AtCoderProblem(onlinejudge.type.Problem):
    """
    :ivar contest_id: :py:class:`str`
    :ivar problem_id: :py:class:`str`

    :note: AtCoder has problems independently from contests. Therefore the notions `contest_id`, `alphabet`, and `url` don't belong to problems itself.
    """
    def __init__(self, *, contest_id: str, problem_id: str):
        self.contest_id = contest_id
        self.problem_id = problem_id  # NOTE: AtCoder calls this as "task_screen_name"
        self._cached_content = None  # type: Union[None, AtCoderProblemContentPartial, AtCoderProblemContent]

    @classmethod
    def _from_table_row(cls, tr: bs4.Tag) -> 'AtCoderProblemContentPartial':
        return _AtCoderProblemContentPartial_from_row(tr)

    def download_content(self, *, session: Optional[requests.Session] = None) -> AtCoderProblemContent:
        """
        :raises Exception: if no such problem exists

        .. versionadded:: 6.2.0
        """

        session = session or utils.get_default_session()
        resp = _request('GET', self.get_url(type='beta'), raise_for_status=False, session=session)
        if _list_alert(resp):
            log.warning('are you logged in?')
        resp.raise_for_status()
        self._cached_content = _AtCoderProblemContent_from_html(resp.content.decode(resp.encoding), problem=self, session=session, response=resp)
        return self._cached_content

    def download_sample_cases(self, *, session: Optional[requests.Session] = None) -> List[onlinejudge.type.TestCase]:
        """
        :raises Exception: if no such problem exists
        """
        return self.download_content(session=session).sample_cases

    def get_url(self, *, type: Optional[str] = None, lang: Optional[str] = None) -> str:
        if type is None or type == 'beta':
            url = 'https://atcoder.jp/contests/{}/tasks/{}'.format(self.contest_id, self.problem_id)
        elif type == 'old':
            url = 'http://{}.contest.atcoder.jp/tasks/{}'.format(self.contest_id, self.problem_id)
        else:
            assert False
        if lang is not None:
            url += '?lang={}'.format(lang)
        return url

    def get_service(self) -> AtCoderService:
        return AtCoderService()

    def get_contest(self) -> AtCoderContest:
        return AtCoderContest(contest_id=self.contest_id)

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
            return cls(contest_id=contest_id, problem_id=problem_id)

        # example: https://beta.atcoder.jp/contests/abc073/tasks/abc073_a
        m = re.match(r'^/contests/([\w\-_]+)/tasks/([\w\-_]+)$', utils.normpath(result.path))
        if result.scheme in ('', 'http', 'https') \
                and result.netloc in ('atcoder.jp', 'beta.atcoder.jp') \
                and m:
            contest_id = m.group(1)
            problem_id = m.group(2)
            return cls(contest_id=contest_id, problem_id=problem_id)

        return None

    def download_input_format(self, *, session: Optional[requests.Session] = None) -> Optional[str]:
        """
        :raises Exception: if no such problem exists
        """
        return self.download_content(session=session).input_format

    def get_available_languages(self, *, session: Optional[requests.Session] = None) -> List[Language]:
        """
        :raises NotLoggedInError:
        """
        content = self.download_content(session=session)
        if content.available_languages is None:
            log.error('not logged in')
            raise NotLoggedInError
        return content.available_languages

    def submit_code(self, code: bytes, language_id: LanguageId, *, filename: Optional[str] = None, session: Optional[requests.Session] = None) -> 'AtCoderSubmission':
        """
        :raises NotLoggedInError:
        :raises SubmissionError:
        """

        session = session or utils.get_default_session()
        assert language_id in [language.id for language in self.get_available_languages(session=session)]

        # get
        url = 'https://atcoder.jp/contests/{}/submit'.format(self.contest_id)
        resp = _request('GET', url, session=session)

        # check whether logged in
        if 'login' in resp.url:
            raise NotLoggedInError

        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        form = soup.find('form', action='/contests/{}/submit'.format(self.contest_id))
        if not form:
            raise SubmissionError('something wrong')
        log.debug('form: %s', str(form))

        # post
        form = utils.FormSender(form, url=resp.url)
        form.set('data.TaskScreenName', self.problem_id)
        form.set('data.LanguageId', str(language_id))
        form.set('sourceCode', code)
        resp = form.request(session=session)
        _list_alert(resp, print_=True)

        # result
        if '/submissions/me' in resp.url:
            submission = next(AtCoderContest(contest_id=self.contest_id)._iterate_submission_contents_from_response(resp=resp)).submission
            log.success('success: result: %s', submission.get_url())
            return submission
        else:
            raise SubmissionError('it may be a rate limit')

    def get_name(self, *, session: Optional[requests.Session] = None) -> str:
        return self.download_content(session=session).name

    def iterate_submissions(self, *, session: Optional[requests.Session] = None) -> Iterator['AtCoderSubmission']:
        """
        :note: in implementation, use "ORDER BY created DESC" to list all submissions even when there are new submissions
        """
        yield from self.get_contest().iterate_submissions_where(problem_id=self.problem_id, order='created', desc=False, session=session)

    def iterate_submissions_where(self, **kwargs) -> Iterator['AtCoderSubmission']:
        yield from self.get_contest().iterate_submissions_where(problem_id=self.problem_id, **kwargs)


AtCoderSubmissionContentPartial = NamedTuple('AtCoderSubmissionContentPartial', [
    ('tag', bs4.Tag),
    ('problem', AtCoderProblem),
    ('submission', 'AtCoderSubmission'),
    ('problem_id', str),
    ('user_id', str),
    ('language_name', str),
    ('score', float),
    ('code_size', int),
    ('status', str),
    ('exec_time_msec', Optional[int]),
    ('memory_byte', Optional[int]),
])

AtCoderSubmissionContent = NamedTuple('AtCoderSubmissionContent', [
    ('session', requests.Session),
    ('response', requests.Response),
    ('problem', AtCoderProblem),
    ('submission', 'AtCoderSubmission'),
    ('problem_id', str),
    ('source_code', bytes),
    ('submission_time', datetime.datetime),
    ('user_id', str),
    ('language_name', str),
    ('score', float),
    ('code_size', int),
    ('status', str),
    ('exec_time_msec', Optional[int]),
    ('memory_byte', Optional[int]),
    ('compile_error', Optional[str]),
    ('test_sets', Optional[List['AtCoderSubmissionTestSet']]),
    ('test_cases', Optional[List['AtCoderSubmissionTestCaseResult']]),
])


class AtCoderSubmission(onlinejudge.type.Submission):
    """
    :ivar contest_id: :py:class:`str`
    :ivar submission_id: :py:class:`str`
    """
    def __init__(self, *, contest_id: str, submission_id: int):
        self.contest_id = contest_id
        self.submission_id = submission_id

    @classmethod
    def _from_table_row(cls, tr: bs4.Tag, *, contest_id: str) -> AtCoderSubmissionContentPartial:
        tds = tr.find_all('td')
        assert len(tds) in (8, 10)

        self = cls.from_url('https://atcoder.jp' + tds[-1].find('a')['href'])
        problem = AtCoderProblem.from_url('https://atcoder.jp' + tds[1].find('a')['href'])
        assert self is not None
        assert problem is not None

        submission_time = datetime.datetime.strptime(tds[0].text, '%Y-%m-%d %H:%M:%S+0900').replace(tzinfo=utils.tzinfo_jst)
        problem_id = problem.problem_id
        user_id = tds[2].find_all('a')[0]['href'].split('/')[-1]
        language_name = tds[3].text
        score = float(tds[4].text)
        code_size = int(utils.remove_suffix(tds[5].text, ' Byte'))
        status = tds[6].text
        if len(tds) == 10:
            exec_time_msec = int(utils.remove_suffix(tds[7].text, ' ms'))  # type: Optional[int]
            memory_byte = int(utils.remove_suffix(tds[8].text, ' KB')) * 1000  # type: Optional[int]
        else:
            exec_time_msec = None
            memory_byte = None
        return AtCoderSubmissionContentPartial(
            tag=tr,
            problem=problem,
            submission=self,
            problem_id=problem_id,
            user_id=user_id,
            language_name=language_name,
            score=score,
            code_size=code_size,
            status=status,
            exec_time_msec=exec_time_msec,
            memory_byte=memory_byte,
        )

    @classmethod
    def from_url(cls, s: str) -> Optional['AtCoderSubmission']:
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
                return cls(contest_id=contest_id, submission_id=submission_id)

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
                return cls(contest_id=contest_id, submission_id=submission_id)

        return None

    def get_url(self, *, type: Optional[str] = None, lang: Optional[str] = None) -> str:
        if type is None or type == 'beta':
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

    def download_problem(self, *, session: Optional[requests.Session] = None) -> AtCoderProblem:
        problem_id = self.download_content(session=session).problem_id
        return AtCoderProblem(contest_id=self.contest_id, problem_id=problem_id)

    def get_problem(self) -> AtCoderProblem:
        """
        :raises Exception:
        :note: There is no way to reconstruct problem_id without networking
        """
        raise Exception

    def download_content(self, *, session: Optional[requests.Session] = None) -> AtCoderSubmissionContent:
        """
        :note: `Exec Time` is undefined when the status is `RE` or `TLE`
        :note: `Memory` is undefined when the status is `RE` or `TLE`
        """
        session = session or utils.get_default_session()
        resp = _request('GET', self.get_url(type='beta', lang='en'), session=session)
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)

        # Submission #N
        id_, = soup.find_all('span', class_='h2')
        assert id_.text == 'Submission #{}'.format(self.submission_id)

        # Source Code
        source_code = soup.find(id='submission-code')
        source_code = source_code.text.encode()

        # get tables
        tables = soup.find_all('table')
        if len(tables) == 3:
            submission_info, test_cases_summary, test_cases_data = tables
        elif len(tables) == 1:
            submission_info, = tables
            test_cases_summary = None
            test_cases_data = None
        else:
            assert False

        # Submission Info
        data = {}  # type: Dict[str, str]
        problem_id = None  # type: Optional[str]
        for tr in submission_info.find_all('tr'):
            key = tr.find('th').text.strip()
            value = tr.find('td').text.strip()
            data[key] = value

            if key == 'Task':
                problem = AtCoderProblem.from_url('https://atcoder.jp' + tr.find('a')['href'])
                assert problem is not None
                problem_id = problem.problem_id

        assert problem_id is not None
        submission_time = datetime.datetime.strptime(data['Submission Time'], '%Y-%m-%d %H:%M:%S+0900').replace(tzinfo=utils.tzinfo_jst)
        user_id = data['User']
        language_name = data['Language']
        score = float(data['Score'])
        code_size = int(utils.remove_suffix(data['Code Size'], ' Byte'))
        status = data['Status']
        if 'Exec Time' in data:
            exec_time_msec = int(utils.remove_suffix(data['Exec Time'], ' ms'))  # type: Optional[int]
        else:
            exec_time_msec = None
        if 'Memory' in data:
            # TODO: confirm this is KB truly, not KiB
            memory_byte = int(utils.remove_suffix(data['Memory'], ' KB')) * 1000  # type: Optional[int]
        else:
            memory_byte = None

        # Compile Error
        compile_error_tag = soup.find('h4', text='Compile Error')
        if compile_error_tag is not None:
            compile_error = compile_error_tag.find_next_sibling('pre').text
        else:
            compile_error = None

        # Test Cases
        if test_cases_summary is not None:
            trs = test_cases_summary.find('tbody').find_all('tr')
            test_sets = [AtCoderSubmissionTestSet._from_table_row(tr) for tr in trs]  # type: Optional[List[AtCoderSubmissionTestSet]]
        else:
            test_sets = None
        if test_cases_data is not None:
            trs = test_cases_data.find('tbody').find_all('tr')
            test_cases = [AtCoderSubmissionTestCaseResult._from_table_row(tr) for tr in trs]  # type: Optional[List[AtCoderSubmissionTestCaseResult]]
        else:
            test_cases = None

        return AtCoderSubmissionContent(
            session=session,
            response=resp,
            problem=AtCoderProblem(contest_id=self.contest_id, problem_id=problem_id),
            submission=self,
            problem_id=problem_id,
            source_code=source_code,
            submission_time=submission_time,
            user_id=user_id,
            language_name=language_name,
            score=score,
            code_size=code_size,
            status=status,
            exec_time_msec=exec_time_msec,
            memory_byte=memory_byte,
            compile_error=compile_error,
            test_sets=test_sets,
            test_cases=test_cases,
        )


class AtCoderSubmissionTestSet(object):
    """
    :ivar set_name: :py:class:`str`
    :ivar score: :py:class:`float`
    :ivar max_score: :py:class:`float`
    :ivar test_case_names: :py:class:`List` [ :py:class:`str` ]
    """
    def __init__(self, *, set_name: str, score: float, max_score: float, test_case_names: List[str]):
        self.set_name = set_name
        self.score = score
        self.max_score = max_score
        self.test_case_names = test_case_names

    @classmethod
    def _from_table_row(cls, tr: bs4.Tag) -> 'AtCoderSubmissionTestSet':
        tds = tr.find_all('td')
        assert len(tds) == 3
        set_name = tds[0].text
        score, max_score = [float(s) for s in tds[1].text.split('/')]
        test_case_names = tds[2].text.split(', ')
        return AtCoderSubmissionTestSet(set_name=set_name, score=score, max_score=max_score, test_case_names=test_case_names)


class AtCoderSubmissionTestCaseResult(object):
    """
    :ivar case_name: :py:class:`str`
    :ivar status: :py:class:`str`
    :ivar exec_time_msec: :py:class:`int` in millisecond
    :ivar memory_byte: :py:class:`int` in byte
    """
    def __init__(self, *, case_name: str, status: str, exec_time_msec: Optional[int], memory_byte: Optional[int]):
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
        return AtCoderSubmissionTestCaseResult(case_name=case_name, status=status, exec_time_msec=exec_time_msec, memory_byte=memory_byte)


onlinejudge.dispatch.services += [AtCoderService]
onlinejudge.dispatch.problems += [AtCoderProblem]
onlinejudge.dispatch.submissions += [AtCoderSubmission]
