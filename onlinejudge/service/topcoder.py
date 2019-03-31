# Python Version: 3.x
"""
the module for Topcoder (https://www.topcoder.com/)

:note: There is the offcial API https://tcapi.docs.apiary.io/
:note: only the Marathon Match is supported
"""

import collections
import itertools
import json
import posixpath
import re
import time
import urllib.parse
import xml.etree.ElementTree
from typing import *

import bs4
import requests

import onlinejudge._implementation.logging as log
import onlinejudge._implementation.utils as utils
import onlinejudge.dispatch
import onlinejudge.type
from onlinejudge.type import *


class TopcoderService(onlinejudge.type.Service):
    def login(self, get_credentials: onlinejudge.type.CredentialsProvider, session: Optional[requests.Session] = None) -> None:
        """
        :raises LoginError:
        """
        session = session or utils.get_default_session()

        # NOTE: you can see this login page with https://community.topcoder.com/longcontest/?module=Submit
        url = 'https://community.topcoder.com/longcontest/'
        username, password = get_credentials()
        data = {
            'nextpage': 'https://www.topcoder.com/',
            'module': 'Login',
            'ha': username,
            'pass': password,
            'rem': 'on',
        }
        resp = utils.request('POST', url, session=session, data=data)

        if 'longcontest' not in resp.url:
            log.success('Success')
        else:
            log.failure('Failure')
            raise LoginError

    def is_logged_in(self, session: Optional[requests.Session] = None) -> bool:
        """
        .. versionadded:: 6.2.0
        """
        session = session or utils.get_default_session()
        url = 'https://community.topcoder.com/longcontest/stats/?module=ViewSystemTest&rd=17143&pm=14889&tid=33800773'
        resp = utils.request('GET', url, session=session)
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        return soup.find('form', attrs={'name': 'frmLogin'}) is None

    def get_url(self) -> str:
        return 'https://www.topcoder.com/'

    def get_name(self) -> str:
        return 'Topcoder'

    @classmethod
    def from_url(cls, url: str) -> Optional['TopcoderService']:
        # example: https://www.topcoder.com/
        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc in ['www.topcoder.com', 'community.topcoder.com']:
            return cls()
        return None


TopcoderLongContestProblemStandingsRow = NamedTuple('TopcoderLongContestProblemStandingsRow', [
    ('handle', str),
    ('score', Optional[float]),
    ('rank', Optional[int]),
    ('last_submission_time', Optional[str]),
    ('language', Optional[str]),
    ('example_tests', int),
    ('submissions', int),
    ('cr', int),
])

TopcoderLongContestProblemOverviewRow = NamedTuple('TopcoderLongContestProblemOverviewRow', [
    ('rank', int),
    ('handle', str),
    ('provisional_rank', int),
    ('provisional_score', float),
    ('final_score', float),
    ('language', str),
    ('cr', int),
])

TopcoderLongContestProblemIndividualResultsFeedSubmission = NamedTuple('TopcoderLongContestProblemIndividualResultsFeedSubmission', [
    ('number', int),
    ('score', float),
    ('language', str),
    ('time', str),
])

TopcoderLongContestProblemIndividualResultsFeedTestCase = NamedTuple('TopcoderLongContestProblemIndividualResultsFeedTestCase', [
    ('test_case_id', int),
    ('score', float),
    ('processing_time', int),
    ('fatal_error_ind', int),
])

TopcoderLongContestProblemIndividualResultsFeed = NamedTuple('TopcoderLongContestProblemIndividualResultsFeed', [
    ('round_id', int),
    ('coder_id', int),
    ('handle', str),
    ('submissions', List[TopcoderLongContestProblemIndividualResultsFeedSubmission]),
    ('testcases', List[TopcoderLongContestProblemIndividualResultsFeedTestCase]),
])


class TopcoderLongContestProblem(onlinejudge.type.Problem):
    def __init__(self, rd, cd=None, compid=None, pm=None):
        self.rd = rd
        self.cd = cd
        self.compid = compid
        self.pm = pm

    def get_url(self) -> str:
        return 'https://community.topcoder.com/tc?module=MatchDetails&rd=' + str(self.rd)

    def get_service(self) -> TopcoderService:
        return TopcoderService()

    def download_sample_cases(self, session: Optional[requests.Session] = None) -> List[onlinejudge.type.TestCase]:
        """
        :raises NotImplementedError:
        """
        raise NotImplementedError

    @classmethod
    def from_url(cls, url: str) -> Optional['TopcoderLongContestProblem']:
        # example: https://community.topcoder.com/longcontest/?module=ViewProblemStatement&rd=16997&pm=14690
        # example: https://community.topcoder.com/longcontest/?module=ViewProblemStatement&rd=16997&compid=57374
        # example: https://community.topcoder.com/longcontest/?module=ViewStandings&rd=16997
        # example: https://community.topcoder.com/tc?module=MatchDetails&rd=16997
        result = urllib.parse.urlparse(url)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'community.topcoder.com' \
                and utils.normpath(result.path) in ['/longcontest', '/tc']:
            querystring = dict(urllib.parse.parse_qsl(result.query))
            if 'rd' in querystring:
                kwargs = {}
                for name in ['rd', 'cd', 'compid', 'pm']:
                    if name in querystring:
                        kwargs[name] = int(querystring[name])
                return cls(**kwargs)
        return None

    def get_available_languages(self, session: Optional[requests.Session] = None) -> List[Language]:
        session = session or utils.get_default_session()

        return [
            Language(LanguageId('1'), 'Java 8'),
            Language(LanguageId('3'), 'C++11'),
            Language(LanguageId('4'), 'C#'),
            Language(LanguageId('5'), 'VB'),
            Language(LanguageId('6'), 'Python 2'),
        ]

    def submit_code(self, code: bytes, language_id: LanguageId, filename: Optional[str] = None, session: Optional[requests.Session] = None, kind: str = 'example') -> onlinejudge.type.Submission:
        """
        :param kind: must be one of `example` (default) or `full`
        :raises NotLoggedInError:
        :raises SubmissionError:
        """

        assert kind in ['example', 'full']
        session = session or utils.get_default_session()

        # TODO: implement self.is_logged_in()
        # if not self.is_logged_in(session=session):
        #     raise NotLoggedInError

        # module=MatchDetails
        url = 'https://community.topcoder.com/tc?module=MatchDetails&rd=%d' % self.rd
        resp = utils.request('GET', url, session=session)
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        path = soup.find('a', text='Register/Submit').attrs['href']
        assert path.startswith('/') and 'module=ViewReg' in path

        # module=ViewActiveContests
        url = 'https://community.topcoder.com' + path
        resp = utils.request('GET', url, session=session)
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        path = [tag.attrs['href'] for tag in soup.find_all('a', text='Submit') if ('rd=%d' % self.rd) in tag.attrs['href']]
        if len(path) == 0:
            log.error('link to submit not found:  Are you logged in?  Are you registered?  Is the contest running?')
            raise SubmissionError('something wrong')
        assert len(path) == 1
        path = path[0]
        assert path.startswith('/') and 'module=Submit' in path
        query = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(path).query))
        self.cd = query['cd']
        self.compid = query['compid']

        # module=Submit
        submit_url = 'https://community.topcoder.com' + path
        resp = utils.request('GET', submit_url, session=session)
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)

        # post
        url = 'https://community.topcoder.com/longcontest/'
        data = {
            'module': 'Submit',
            'rd': self.rd,
            'cd': self.cd,
            'compid': self.compid,
            'Action': 'submit',
            'exOn': {
                'example': 'true',
                'full': 'false'
            }[kind],
            'lid': str(language_id),
            'code': code,
        }
        resp = utils.request('POST', url, session=session, data=data)

        # check if module=SubmitSuccess
        if 'module=SubmitSuccess' in resp.content.decode(resp.encoding):
            url = 'http://community.topcoder.com/longcontest/?module=SubmitSuccess&rd={}&cd={}&compid={}'.format(self.rd, self.cd, self.compid)
            log.success('success: result: %s', url)
            return utils.DummySubmission(url, problem=self)
        else:
            # module=Submit to get error messages
            resp = utils.request('GET', submit_url, session=session)
            soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
            messages = soup.find('textarea', {'name': 'messages'}).text
            log.failure('%s', messages)
            raise SubmissionError('it may be a rate limit: ' + messages)

    def download_standings(self, session: Optional[requests.Session] = None) -> List[TopcoderLongContestProblemStandingsRow]:
        """
        :raises Exception: if redirected to `module=ViewOverview` page

        .. versionadded:: 6.2.0
            This method may be deleted in future.
        """
        session = session or utils.get_default_session()

        rows = []  # type: List[TopcoderLongContestProblemStandingsRow]
        for start in itertools.count(1):
            # get
            url = 'https://community.topcoder.com/longcontest/?module=ViewStandings&rd={}&nr=100&sr={}'.format(self.rd, start)
            resp = utils.request('GET', url, allow_redirects=False, session=session)
            if resp.status_code != 200:
                raise RuntimeError('failed to get {}'.format(url))

            # parse
            soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
            table = soup.find('table', class_='statTable')
            for tr in table.find_all('tr')[2:]:  # NOTE: first two rows are headings
                row = collections.OrderedDict()  # type: Dict[str, str]
                tds = tr.find_all('td')
                texts = [td.text.strip() for td in tds]  # NOTE: some cells may be empty strings

                assert len(texts) == 7
                handle = texts[0]
                score = float(texts[1]) if texts[1] else None
                rank = int(texts[2]) if texts[2] else None
                last_submission_time = texts[3] or None
                language = texts[4] or None
                example_tests = int(tds[5].text)
                submissions = int(tds[6].text)
                href = (tds[5].find('a') or tds[6].find('a')).attrs['href']
                query = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(href).query))
                self.compid = query['compid']
                rows += [TopcoderLongContestProblemStandingsRow(handle, score, rank, last_submission_time, language, example_tests, submissions, cr=int(query['cr']))]

            # check whether the next page exists
            link = soup.find('a', text='next >>')
            if link is None:
                break

        return rows

    def download_overview(self, session: Optional[requests.Session] = None) -> List[TopcoderLongContestProblemOverviewRow]:
        """
        .. versionadded:: 6.2.0
            This method may be deleted in future.
        """
        session = session or utils.get_default_session()

        # get
        number = 9999
        start = 1
        url = 'https://community.topcoder.com/longcontest/stats/?module=ViewOverview&rd={}&nr={}&sr={}'.format(self.rd, number, start)
        resp = utils.request('GET', url, session=session)

        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        table = soup.find('table', class_='stat')
        overview = []  # type: List[TopcoderLongContestProblemOverviewRow]
        for tr in table.find_all('tr', class_=re.compile(r'light|dark')):
            tds = tr.find_all('td')
            assert len(tds) == 9
            rank = int(tds[0].text)
            handle = tds[1].text.strip()
            provisional_rank = int(tds[2].text)
            provisional_score = float(tds[3].text)
            final_score = float(tds[4].text)
            language = tds[5].text.strip()
            assert tds[6].text.strip() == 'results'
            assert tds[7].text.strip() == 'submission history'
            assert tds[8].text.strip() == 'example history'
            query = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(tds[6].find('a').attrs['href']).query))
            self.pm = query['pm']
            overview += [TopcoderLongContestProblemOverviewRow(rank, handle, provisional_rank, provisional_score, final_score, language, cr=int(query['cr']))]
        return overview

    def download_individual_results_feed(self, cr: int, session: Optional[requests.Session] = None) -> TopcoderLongContestProblemIndividualResultsFeed:
        """
        .. versionadded:: 6.2.0
            This method may be deleted in future.
        """
        session = session or utils.get_default_session()

        # get
        url = 'https://community.topcoder.com/longcontest/stats/?module=IndividualResultsFeed&rd={}&cr={}'.format(self.rd, cr)
        resp = utils.request('GET', url, session=session)

        # parse
        def get_text_at(node: xml.etree.ElementTree.Element, i: int) -> str:
            text = list(node)[i].text
            if text is None:
                raise ValueError
            return text

        root = xml.etree.ElementTree.fromstring(resp.content.decode(resp.encoding))
        assert len(list(root)) == 5
        round_id = int(get_text_at(root, 0))
        coder_id = int(get_text_at(root, 1))
        handle = get_text_at(root, 2)
        submissions = []  # type: List[TopcoderLongContestProblemIndividualResultsFeedSubmission]
        for submission in list(root)[3]:
            number = int(get_text_at(submission, 0))
            score = float(get_text_at(submission, 1))
            language = get_text_at(submission, 2)
            time = get_text_at(submission, 3)
            submissions += [TopcoderLongContestProblemIndividualResultsFeedSubmission(number, score, language, time)]
        testcases = []  # type: List[TopcoderLongContestProblemIndividualResultsFeedTestCase]
        for testcase in list(root)[4]:
            test_case_id = int(get_text_at(testcase, 0))
            score = float(get_text_at(testcase, 1))
            processing_time = int(get_text_at(testcase, 2))
            fatal_error_ind = int(get_text_at(testcase, 3))
            testcases += [TopcoderLongContestProblemIndividualResultsFeedTestCase(test_case_id, score, processing_time, fatal_error_ind)]
        return TopcoderLongContestProblemIndividualResultsFeed(round_id, coder_id, handle, submissions, testcases)

    def download_system_test(self, test_case_id: int, session: Optional[requests.Session] = None) -> str:
        """
        :raises NotLoggedInError:
        :note: You need to parse this result manually.

        .. versionadded:: 6.2.0
            This method may be deleted in future.
        """
        session = session or utils.get_default_session()

        # get
        assert self.pm is not None
        url = 'https://community.topcoder.com/longcontest/stats/?module=ViewSystemTest&rd={}&pm={}&tid={}'.format(self.rd, self.pm, test_case_id)
        resp = utils.request('GET', url, session=session)

        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        if soup.find('form', attrs={'name': 'frmLogin'}):
            raise NotLoggedInError
        return soup.find('pre').text


onlinejudge.dispatch.services += [TopcoderService]
onlinejudge.dispatch.problems += [TopcoderLongContestProblem]
