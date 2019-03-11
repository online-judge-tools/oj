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
        :raises NotImplementedError:
        """
        raise NotImplementedError

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

    def get_standings(self, session: Optional[requests.Session] = None) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        .. deprecated:: 6.0.0
            This method may be deleted in future.
        """
        session = session or utils.get_default_session()

        header = None  # type: Optional[List[str]]
        rows = []  # type: List[Dict[str, str]]
        for start in itertools.count(1, 100):
            # get
            url = 'https://community.topcoder.com/longcontest/?sc=&sd=&nr=100&sr={}&rd={}&module=ViewStandings'.format(start, self.rd)
            resp = utils.request('GET', url, session=session)

            # parse
            soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
            table = soup.find('table', class_='statTable')
            trs = table.find_all('tr')
            if header is None:
                tr = trs[1]
                header = [td.text.strip() for td in tr.find_all('td')]
            for tr in trs[2:]:
                row = collections.OrderedDict()  # type: Dict[str, str]
                for key, td in zip(header, tr.find_all('td')):
                    value = td.text.strip()
                    if not value:
                        value = None
                    elif value.isdigit():
                        value = int(value)
                    row[key] = value
                rows += [row]

            # check whether the next page exists
            link = soup.find('a', text='next >>')
            if link is None:
                break

        assert header is not None
        return header, rows


onlinejudge.dispatch.services += [TopcoderService]
onlinejudge.dispatch.problems += [TopcoderLongContestProblem]
