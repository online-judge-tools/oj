# Python Version: 3.x
import onlinejudge.service
import onlinejudge.problem
import onlinejudge.dispatch
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import re
import urllib.parse
import posixpath
import bs4
import string


@utils.singleton
class CodeforcesService(onlinejudge.service.Service):

    def login(self, get_credentials, session=None):
        session = session or utils.new_default_session()
        url = 'http://codeforces.com/enter'
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
        form.set('handle', username)
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

    def get_url(self):
        return 'http://codeforces.com/'

    def get_name(self):
        return 'codeforces'

    @classmethod
    def from_url(cls, s):
        # example: http://codeforces.com/
        result = urllib.parse.urlparse(s)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'codeforces.com':
            return cls()


# NOTE: Codeforces has its API: http://codeforces.com/api/help
class CodeforcesProblem(onlinejudge.problem.Problem):
    def __init__(self, contest_id, index, kind=None):
        assert isinstance(contest_id, int)
        assert index in string.ascii_uppercase
        self.contest_id = contest_id
        self.index = index
        self.kind = kind  # It seems 'gym' is specialized, 'contest' and 'problemset' are the same thing
        if kind is None:
            if self.contest_id < 100000:
                self.kind = 'contest'
            else:
                self.kind = 'gym'

    def download(self, session=None):
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
            samples.add(s, title.string)
        return samples.get()

    def get_url(self):
        table = {}
        table['contest']    = 'http://codeforces.com/contest/{}/problem/{}'
        table['problemset'] = 'http://codeforces.com/problemset/problem/{}/{}'
        table['gym']        = 'http://codeforces.com/gym/{}/problem/{}'
        return table[self.kind].format(self.contest_id, self.index)

    def get_service(self):
        return CodeforcesService()

    @classmethod
    def from_url(cls, s):
        result = urllib.parse.urlparse(s)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'codeforces.com':
            table = {}
            table['contest']    = r'^/contest/([0-9]+)/problem/([0A-Za-z])$'  # example: http://codeforces.com/contest/538/problem/H
            table['problemset'] = r'^/problemset/problem/([0-9]+)/([0A-Za-z])$'  # example: http://codeforces.com/problemset/problem/700/B
            table['gym']        = r'^/gym/([0-9]+)/problem/([0A-Za-z])$'  # example: http://codeforces.com/gym/101021/problem/A
            normalize = lambda c: c == '0' and 'A' or c.upper()
            for kind, expr in table.items():
                m = re.match(expr, utils.normpath(result.path))
                if m:
                    return cls(int(m.group(1)), normalize(m.group(2)), kind=kind)


onlinejudge.dispatch.services += [ CodeforcesService ]
onlinejudge.dispatch.problems += [ CodeforcesProblem ]
