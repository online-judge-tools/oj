# Python Version: 3.x
import onlinejudge.type
from onlinejudge.type import SubmissionError
import onlinejudge.dispatch
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import requests
import re
import urllib.parse
import posixpath
import bs4
import string
from typing import *


@utils.singleton
class CodeforcesService(onlinejudge.type.Service):

    def login(self, get_credentials: onlinejudge.type.CredentialsProvider, session: Optional[requests.Session] = None) -> bool:
        session = session or utils.new_default_session()
        url = 'https://codeforces.com/enter'
        # get
        resp = utils.request('GET', url, session=session)
        if resp.url != url:  # redirected
            log.info('You have already signed in.')
            return True
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
            return True
        else:
            log.failure('Invalid handle or password.')
            return False

    def get_url(self) -> str:
        return 'https://codeforces.com/'

    def get_name(self) -> str:
        return 'codeforces'

    @classmethod
    def from_url(cls, s: str) -> Optional['CodeforcesService']:
        # example: https://codeforces.com/
        # example: http://codeforces.com/
        result = urllib.parse.urlparse(s)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'codeforces.com':
            return cls()
        return None


# NOTE: Codeforces has its API: https://codeforces.com/api/help
class CodeforcesProblem(onlinejudge.type.Problem):
    def __init__(self, contest_id: int, index: str, kind: Optional[str] = None):
        assert isinstance(contest_id, int)
        assert index in string.ascii_uppercase
        assert kind in ( None, 'contest', 'gym', 'problemset' )
        self.contest_id = contest_id
        self.index = index
        if kind is None:
            if self.contest_id < 100000:
                kind = 'contest'
            else:
                kind = 'gym'
        self.kind = kind  # It seems 'gym' is specialized, 'contest' and 'problemset' are the same thing

    def download_sample_cases(self, session: Optional[requests.Session] = None) -> List[onlinejudge.type.TestCase]:
        session = session or utils.new_default_session()
        # get
        resp = utils.request('GET', self.get_url(), session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        samples = utils.SampleZipper()
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
            samples.add(s, title.string)
        return samples.get()

    def get_language_dict(self, session: Optional['requests.Session'] = None) -> Dict[str, onlinejudge.type.Language]:
        session = session or utils.new_default_session()
        # get
        resp = utils.request('GET', self.get_url(), session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        select = soup.find('select', attrs={ 'name': 'programTypeId' })
        if select is None:
            log.error('not logged in')
            return {}
        language_dict = {}
        for option in select.findAll('option'):
            language_dict[option.attrs['value']] = { 'description': option.string }
        return language_dict

    def submit_code(self, code: bytes, language: str, session: Optional['requests.Session'] = None) -> onlinejudge.type.Submission:  # or SubmissionError
        session = session or utils.new_default_session()
        # get
        resp = utils.request('GET', self.get_url(), session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        form = soup.find('form', class_='submitForm')
        if form is None:
            log.error('not logged in')
            raise SubmissionError
        log.debug('form: %s', str(form))
        # make data
        form = utils.FormSender(form, url=resp.url)
        form.set('programTypeId', language)
        form.set_file('sourceFile', 'code', code)
        resp = form.request(session=session)
        resp.raise_for_status()
        # result
        if resp.url.endswith('/my'):
            # example: https://codeforces.com/contest/598/my
            log.success('success: result: %s', resp.url)
            return onlinejudge.type.DummySubmission(resp.url)
        else:
            log.failure('failure')
            log.debug('redirected to %s', resp.url)
            # parse error messages
            soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
            for span in soup.findAll('span', class_='error'):
                log.warning('Codeforces says: "%s"', span.string)
            raise SubmissionError

    def get_url(self) -> str:
        table = {}
        table['contest']    = 'https://codeforces.com/contest/{}/problem/{}'
        table['problemset'] = 'https://codeforces.com/problemset/problem/{}/{}'
        table['gym']        = 'https://codeforces.com/gym/{}/problem/{}'
        return table[self.kind].format(self.contest_id, self.index)

    def get_service(self) -> CodeforcesService:
        return CodeforcesService()

    @classmethod
    def from_url(cls, s: str) -> Optional['CodeforcesProblem']:
        result = urllib.parse.urlparse(s)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'codeforces.com':
            table = {}
            table['contest']    = r'^/contest/([0-9]+)/problem/([0A-Za-z])$'  # example: https://codeforces.com/contest/538/problem/H
            table['problemset'] = r'^/problemset/problem/([0-9]+)/([0A-Za-z])$'  # example: https://codeforces.com/problemset/problem/700/B
            table['gym']        = r'^/gym/([0-9]+)/problem/([0A-Za-z])$'  # example: https://codeforces.com/gym/101021/problem/A
            normalize = (lambda c: c == '0' and 'A' or c.upper())
            for kind, expr in table.items():
                m = re.match(expr, utils.normpath(result.path))
                if m:
                    return cls(int(m.group(1)), normalize(m.group(2)), kind=kind)
        return None


onlinejudge.dispatch.services += [ CodeforcesService ]
onlinejudge.dispatch.problems += [ CodeforcesProblem ]
