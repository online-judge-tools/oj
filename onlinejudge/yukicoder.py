# Python Version: 3.x
import onlinejudge.service
import onlinejudge.problem
import onlinejudge.submission
import onlinejudge.dispatch
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import re
import io
import os.path
import posixpath
import bs4
import requests
import urllib.parse
import zipfile
import collections


@utils.singleton
class YukicoderService(onlinejudge.service.Service):

    def login(self, get_credentials, session=None, method=None):
        if method == 'github':
            return self.login_with_github(get_credentials, session=session)
        elif method == 'twitter':
            return self.login_with_twitter(get_credentials, session=session)
        else:
            assert False

    def login_with_github(self, get_credentials, session=None):
        session = session or requests.Session()
        url = 'https://yukicoder.me/auth/github'
        # get
        log.status('GET: %s', url)
        resp = session.get(url)
        log.status(utils.describe_status_code(resp.status_code))
        resp.raise_for_status()
        if urllib.parse.urlparse(resp.url).hostname == 'yukicoder.me':
            log.info('You have already signed in.')
            return True
        # redirect to github.com
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        form = soup.find('form')
        if not form:
            log.error('form not found')
            log.info('Did you logged in?')
            return False
        log.debug('form: %s', str(form))
        # post
        username, password = get_credentials()
        form = utils.FormSender(form, url=resp.url)
        form.set('login', username)
        form.set('password', password)
        resp = form.request(session)
        resp.raise_for_status()
        if urllib.parse.urlparse(resp.url).hostname == 'yukicoder.me':
            log.success('You signed in.')
            return True
        else:
            log.failure('You failed to sign in. Wrong user ID or password.')
            return False

    def login_with_twitter(self, get_credentials, session=None):
        session = session or requests.Session()
        url = 'https://yukicoder.me/auth/twitter'
        raise NotImplementedError

    def get_url(self):
        return 'https://yukicoder.me/'

    def get_name(self):
        return 'yukicoder'

    @classmethod
    def from_url(cls, s):
        # example: http://yukicoder.me/
        result = urllib.parse.urlparse(s)
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'yukicoder.me':
            return cls()


class YukicoderProblem(onlinejudge.problem.Problem):
    def __init__(self, problem_no=None, problem_id=None):
        assert problem_no or problem_id
        assert not problem_no or isinstance(problem_no, int)
        assert not problem_id or isinstance(problem_id, int)
        self.problem_no = problem_no
        self.problem_id = problem_id

    def download(self, session=None, is_system=False):
        if is_system:
            return self.download_system(session=session)
        else:
            return self.download_samples(session=session)
    def download_samples(self, session=None):
        session = session or requests.Session()
        url = self.get_url()
        # get
        log.status('GET: %s', url)
        resp = session.get(url)
        log.status(utils.describe_status_code(resp.status_code))
        resp.raise_for_status()
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        samples = utils.SampleZipper()
        for pre in soup.find_all('pre'):
            log.debug('pre: %s', str(pre))
            it = self._parse_sample_tag(pre)
            if it is not None:
                s, name = it
                samples.add(s, name)
        return samples.get()
    def download_system(self, session=None):
        session = session or requests.Session()
        url = 'https://yukicoder.me/problems/no/{}/testcase.zip'.format(self.problem_no)
        # get
        log.status('GET: %s', url)
        resp = session.get(url)
        log.status(utils.describe_status_code(resp.status_code))
        resp.raise_for_status()
        # parse
        samples = collections.defaultdict(list)
        with zipfile.ZipFile(io.BytesIO(resp.content)) as fh:
            for filename in sorted(fh.namelist()):  # "test_in" < "test_out"
                s = fh.read(filename).decode()
                name = os.path.basename(filename)
                if os.path.splitext(name)[1] == '.in':  # ".in" extension is confusing
                    name = os.path.splitext(name)[0]
                print(filename, name)
                samples[os.path.basename(filename)] += [( s, name )]
        return sorted(samples.values())

    def _parse_sample_tag(self, tag):
        assert isinstance(tag, bs4.Tag)
        assert tag.name == 'pre'
        prv = utils.previous_sibling_tag(tag)
        pprv = tag.parent and utils.previous_sibling_tag(tag.parent)
        if prv.name == 'h6' and tag.parent.name == 'div' and tag.parent['class'] == ['paragraph'] and pprv.name == 'h5':
            log.debug('h6: %s', str(prv))
            log.debug('name.encode(): %s', prv.string.encode())
            s = tag.string or ''  # tag.string for the tag "<pre></pre>" returns None
            return utils.textfile(s.lstrip()), pprv.string + ' ' + prv.string

    def get_url(self):
        if self.problem_no:
            return 'https://yukicoder.me/problems/no/{}'.format(self.problem_no)
        elif self.problem_id:
            return 'https://yukicoder.me/problems/{}'.format(self.problem_id)
        else:
            assert False

    @classmethod
    def from_url(cls, s):
        # example: https://yukicoder.me/problems/no/499
        # example: http://yukicoder.me/problems/1476
        result = urllib.parse.urlparse(s)
        dirname, basename = posixpath.split(utils.normpath(result.path))
        if result.scheme in ('', 'http', 'https') \
                and result.netloc == 'yukicoder.me':
            try:
                n = int(basename)
            except ValueError:
                n = None
            if n is not None:
                if dirname == '/problems/no':
                    return cls(problem_no=int(n))
                if dirname == '/problems':
                    return cls(problem_id=int(n))
            return cls()

    # Fri Jan  6 16:49:14 JST 2017
    _language_dict = {}
    _language_dict['cpp']        = { 'description': 'C++11 (gcc 4.8.5)' }
    _language_dict['cpp14' ]     = { 'description': 'C++14 (gcc 6.2.0)' }
    _language_dict['c']          = { 'description': 'C (gcc 4.8.5)' }
    _language_dict['java8']      = { 'description': 'Java8 (openjdk 1.8.0_111)' }
    _language_dict['csharp']     = { 'description': 'C# (mono 4.6.1)' }
    _language_dict['perl']       = { 'description': 'Perl (5.16.3)' }
    _language_dict['perl6']      = { 'description': 'Perl6 (rakudo 2016.10-114-g8e79509)' }
    _language_dict['php']        = { 'description': 'PHP (5.4.16)' }
    _language_dict['python']     = { 'description': 'Python2 (2.7.11)' }
    _language_dict['python3']    = { 'description': 'Python3 (3.5.1)' }
    _language_dict['pypy2']      = { 'description': 'PyPy2 (4.0.0)' }
    _language_dict['pypy3']      = { 'description': 'PyPy3 (2.4.0)' }
    _language_dict['ruby']       = { 'description': 'Ruby (2.3.1p112)' }
    _language_dict['d']          = { 'description': 'D (dmd 2.071.1)' }
    _language_dict['go']         = { 'description': 'Go (1.7.3)' }
    _language_dict['haskell']    = { 'description': 'Haskell (7.8.3)' }
    _language_dict['scala']      = { 'description': 'Scala (2.11.8)' }
    _language_dict['nim']        = { 'description': 'Nim (0.15.2)' }
    _language_dict['rust']       = { 'description': 'Rust (1.12.1)' }
    _language_dict['kotlin']     = { 'description': 'Kotlin (1.0.2)' }
    _language_dict['scheme']     = { 'description': 'Scheme (Gauche-0.9.4)' }
    _language_dict['crystal']    = { 'description': 'Crystal (0.19.4)' }
    _language_dict['ocaml']      = { 'description': 'OCaml (4.01.1)' }
    _language_dict['fsharp']     = { 'description': 'F# (4.0)' }
    _language_dict['elixir']     = { 'description': 'Elixir (0.12.5)' }
    _language_dict['lua']        = { 'description': 'Lua (LuaJit 2.0.4)' }
    _language_dict['fortran']    = { 'description': 'Fortran (gFortran 4.8.5)' }
    _language_dict['node']       = { 'description': 'JavaScript (node v7.0.0)' }
    _language_dict['vim']        = { 'description': 'Vim script (v8.0.0124)' }
    _language_dict['sh']         = { 'description': 'Bash (Bash 4.2.46)' }
    _language_dict['text']       = { 'description': 'Text (cat 8.22)' }
    _language_dict['nasm']       = { 'description': 'Assembler (nasm 2.10.07)' }
    _language_dict['bf']         = { 'description': 'Brainfuck (BFI 1.1)' }
    _language_dict['Whitespace'] = { 'description': 'Whitespace (0.3)' }
    def get_language_dict(self, session=None):  # TODO: get dynamically
        return self.__class__._language_dict

    def submit(self, code, language, session=None):
        assert language in self.get_language_dict(session=session)
        session = session or requests.Session()
        url = self.get_url() + '/submit'
        # get
        log.status('GET: %s', url)
        resp = session.get(url)
        log.status(utils.describe_status_code(resp.status_code))
        resp.raise_for_status()
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        form = soup.find('form', action=re.compile(r'/submit$'))
        if not form:
            log.error('form not found')
            return None
        log.debug('form: %s', str(form))
        # post
        form = utils.FormSender(form, url=resp.url)
        if False:
            form.set('source', code)
        else:
            form.set_file('file', ('source', code))
        form.set('lang', language)
        resp = form.request(session=session)
        resp.raise_for_status()
        # result
        if '/submissions/' in resp.url:
            log.success('success: result: %s', resp.url)
            return onlinejudge.submission.CompatibilitySubmission(resp.url, problem=self)
        else:
            log.failure('failure')
            return None

    def get_service(self):
        return YukicoderService()

    def get_input_format(self, session=None):
        session = session or requests.Session()
        url = self.get_url()
        # get
        log.status('GET: %s', url)
        resp = session.get(url)
        log.status(utils.describe_status_code(resp.status_code))
        resp.raise_for_status()
        # parse
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        for h4 in soup.find_all('h4'):
            if h4.string == '入力':
                return h4.parent.find('pre').string


onlinejudge.dispatch.services += [ YukicoderService ]
onlinejudge.dispatch.problems += [ YukicoderProblem ]
