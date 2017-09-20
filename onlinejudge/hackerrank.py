# Python Version: 3.x
import onlinejudge.service
import onlinejudge.problem
import onlinejudge.submission
import onlinejudge.dispatch
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import re
import bs4
import requests
import urllib.parse
import posixpath
import json
import datetime
import time


@utils.singleton
class HackerRankService(onlinejudge.service.Service):

    def login(self, get_credentials, session=None):
        session = session or utils.new_default_session()
        url = 'https://www.hackerrank.com/login'
        # get
        resp = utils.request('GET', url, session=session)
        if resp.url != url:
            log.info('You have already signed in.')
            return True
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        form = soup.find('form', id='legacy-login')
        if not form:
            log.error('form not found')
            return False
        csrftoken = soup.find('meta', attrs={ 'name': 'csrf-token' }).attrs['content']
        # post
        username, password = get_credentials()
        form = utils.FormSender(form, url=resp.url)
        form.set('login', username)
        form.set('password', password)
        form.set('remember_me', 'true')
        form.set('fallback', 'true')
        resp = form.request(session, action='/auth/login', headers={ 'X-CSRF-Token': csrftoken })
        resp.raise_for_status()
        # result
        if resp.url != url:
            log.success('You signed in.')
            return True
        else:
            log.failure('You failed to sign in. Wrong user ID or password.')
            return False

    def get_url(self):
        return 'https://www.hackerrank.com/'

    def get_name(self):
        return 'hackerrank'

    @classmethod
    def from_url(cls, s):
        # example: https://www.hackerrank.com/dashboard
        result = urllib.parse.urlparse(s)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc in ('hackerrank.com', 'www.hackerrank.com'):
            return cls()


class HackerRankProblem(onlinejudge.problem.Problem):
    def __init__(self, contest_slug, challenge_slug):
        self.contest_slug = contest_slug
        self.challenge_slug = challenge_slug

    def download(self, session=None, method='run_code'):
        if method == 'run_code':
            return self.download_with_running_code(session=session)
        elif method == 'parse_html':
            return self.download_with_parsing_html(session=session)
        else:
            assert False

    def download_with_running_code(self, session=None):
        session = session or utils.new_default_session()
        # get
        resp = utils.request('GET', self.get_url(), session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        csrftoken = soup.find('meta', attrs={ 'name': 'csrf-token' }).attrs['content']
        # post
        url = 'https://www.hackerrank.com/rest/contests/{}/challenges/{}/compile_tests'.format(self.contest_slug, self.challenge_slug)
        payload = { 'code': ':', 'language': 'bash', 'customtestcase': False }
        log.debug('payload: %s', payload)
        resp = utils.request('POST', url, session=session, json=payload, headers={ 'X-CSRF-Token': csrftoken })
        # parse
        it = json.loads(resp.content.decode())
        log.debug('json: %s', it)
        if not it['status']:
            log.error('Run Code: failed')
            return []
        model_id = it['model']['id']
        now = datetime.datetime.now()
        unixtime = int(datetime.datetime.now().timestamp() * 10**3)
        url = 'https://www.hackerrank.com/rest/contests/{}/challenges/{}/compile_tests/{}?_={}'.format(self.contest_slug, self.challenge_slug, it['model']['id'], unixtime)
        # sleep
        log.status('sleep(3)')
        time.sleep(3)
        # get
        resp = utils.request('GET', url, session=session, headers={ 'X-CSRF-Token': csrftoken })
        # parse
        it = json.loads(resp.content.decode())
        log.debug('json: %s', it)
        if not it['status']:
            log.error('Run Code: failed')
            return []
        samples = []
        for i, (inf, outf) in enumerate(zip(it['model']['stdin'], it['model']['expected_output'])):
            inname  = 'Testcase {} Input'.format(i)
            outname = 'Testcase {} Expected Output'.format(i)
            samples += [ {
                'input': { 'data': utils.textfile(inf), 'name': inname },
                'output': { 'data': utils.textfile(outf), 'name': outname },
                } ]
        return samples


    def download_with_parsing_html(self, session=None):
        session = session or utils.new_default_session()
        url = 'https://www.hackerrank.com/rest/contests/{}/challenges/{}'.format(self.contest_slug, self.challenge_slug)
        raise NotImplementedError

    def get_url(self):
        if self.contest_slug == 'master':
            return 'https://www.hackerrank.com/challenges/{}'.format(self.challenge_slug)
        else:
            return 'https://www.hackerrank.com/contests/{}/challenges/{}'.format(self.contest_slug, self.challenge_slug)

    def get_service(self):
        return HackerRankService()

    @classmethod
    def from_url(cls, s):
        # example: https://www.hackerrank.com/contests/university-codesprint-2/challenges/the-story-of-a-tree
        # example: https://www.hackerrank.com/challenges/fp-hello-world
        result = urllib.parse.urlparse(s)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc in ('hackerrank.com', 'www.hackerrank.com'):
            m = re.match(r'^/contests/([0-9A-Za-z-]+)/challenges/([0-9A-Za-z-]+)$', utils.normpath(result.path))
            if m:
                return cls(m.group(1), m.group(2))
            m = re.match(r'^/challenges/([0-9A-Za-z-]+)$', utils.normpath(result.path))
            if m:
                return cls('master', m.group(1))

    def _get_model(self, session=None):
        session = session or utils.new_default_session()
        # get
        url = 'https://www.hackerrank.com/rest/contests/{}/challenges/{}'.format(self.contest_slug, self.challenge_slug)
        resp = utils.request('GET', url, session=session)
        # parse
        it = json.loads(resp.content.decode())
        log.debug('json: %s', it)
        if not it['status']:
            log.error('get model: failed')
            return None
        return it['model']

    def get_language_dict(self, session=None):
        session = session or utils.new_default_session()
        info = self._get_model(session=session)
        # lang_display_mapping from https://hrcdn.net/hackerrank/assets/codeshell/dist/codeshell-449bb296b091277fedc42b23f7c9c447.js, Sun Feb 19 02:25:36 JST 2017
        lang_display_mapping = { 'c': 'C', 'cpp': 'C++', 'java': 'Java 7', 'csharp': 'C#', 'haskell': 'Haskell', 'php': 'PHP', 'python': 'Python 2', 'pypy': 'Pypy 2', 'pypy3': 'Pypy 3', 'ruby': 'Ruby', 'perl': 'Perl', 'bash': 'BASH', 'oracle': 'Oracle', 'mysql': 'MySQL', 'sql': 'SQL', 'clojure': 'Clojure', 'scala': 'Scala', 'code': 'Generic', 'text': 'Plain Text', 'brainfuck': 'Brainfuck', 'javascript': 'Javascript', 'typescript': 'Typescript', 'lua': 'Lua', 'sbcl': 'Common Lisp (SBCL)', 'erlang': 'Erlang', 'go': 'Go', 'd': 'D', 'ocaml': 'OCaml', 'pascal': 'Pascal', 'python3': 'Python 3', 'groovy': 'Groovy', 'objectivec': 'Objective-C', 'text_pseudo': 'Plain Text', 'fsharp': 'F#', 'visualbasic': 'VB. NET', 'cobol': 'COBOL', 'tsql': 'MS SQL Server', 'lolcode': 'LOLCODE', 'smalltalk': 'Smalltalk', 'tcl': 'Tcl', 'whitespace': 'Whitespace', 'css': 'CSS', 'html': 'HTML', 'java8': 'Java 8', 'db2': 'DB2', 'octave': 'Octave', 'r': 'R', 'xquery': 'XQuery', 'racket': 'Racket', 'xml': 'XML', 'rust': 'Rust', 'swift': 'Swift', 'elixir': 'Elixir', 'fortran': 'Fortran', 'ada': 'Ada', 'nim': 'Nim', 'julia': 'Julia', 'cpp14': 'C++14', 'coffeescript': 'Coffeescript' }
        result = {}
        for lang in info['languages']:
            descr = lang_display_mapping.get(lang)
            if descr is None:
                log.warning('display mapping for language `%s\' not found', lang)
                descr = lang
            result[lang] = { 'description': descr }
        return result

    def submit(self, code, language, session=None):
        session = session or utils.new_default_session()
        # get
        resp = utils.request('GET', self.get_url(), session=session)
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        csrftoken = soup.find('meta', attrs={ 'name': 'csrf-token' }).attrs['content']
        # post
        url = 'https://www.hackerrank.com/rest/contests/{}/challenges/{}/submissions'.format(self.contest_slug, self.challenge_slug)
        payload = { 'code': code, 'language': language }
        log.debug('payload: %s', payload)
        resp = utils.request('POST', url, session=session, json=payload, headers={ 'X-CSRF-Token': csrftoken })
        # parse
        it = json.loads(resp.content.decode())
        log.debug('json: %s', it)
        if not it['status']:
            log.failure('Submit Code: failed')
            return None
        model_id = it['model']['id']
        url = self.get_url().rstrip('/') + '/submissions/code/{}'.format(model_id)
        log.success('success: result: %s', url)
        return onlinejudge.submission.CompatibilitySubmission(url, problem=self)

onlinejudge.dispatch.services += [ HackerRankService ]
onlinejudge.dispatch.problems += [ HackerRankProblem ]
