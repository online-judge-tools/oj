#!/usr/bin/env python3
import onlinejudge.service
import onlinejudge.problem
import onlinejudge.dispatch
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import re
import io
import os.path
import bs4
import requests
import urllib.parse
import zipfile
import collections


@utils.singleton
class YukicoderService(onlinejudge.service.Service):

    def login(self, get_credentials, session=None, method=None):
        if method == 'github':
            return self.login_with_github(session, get_credentials)
        elif method == 'twitter':
            return self.login_with_twitter(session, get_credentials)
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
        return 'http://yukicoder.me/'

    def get_name(self):
        return 'yukicoder'

    @classmethod
    def from_url(cls, s):
        if re.match(r'^https?://yukicoder\.me/?$', s):
            return cls()


class YukicoderProblem(onlinejudge.problem.Problem):
    def __init__(self, problem_no=None, problem_id=None):
        assert problem_no or problem_id
        assert not problem_no or isinstance(problem_no, int)
        assert not problem_id or isinstance(problem_id, int)
        self.problem_no = problem_no
        self.problem_id = problem_id

    def download(self, session=None, is_all=False):
        if is_all:
            return self.download_all(session=session)
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
    def download_all(self, session=None):
        session = session or requests.Session()
        url = 'http://yukicoder.me/problems/no/{}/testcase.zip'.format(self.problem_no)
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
        m = re.match(r'^https?://yukicoder\.me/problems/(no/)?([0-9]+)/?$', s)
        if m:
            n = int(m.group(2).lstrip('0') or '0')
            if m.group(1):
                return cls(problem_no=int(n))
            else:
                return cls(problem_id=int(n))

    # Fri Jan  6 16:49:14 JST 2017
    _languages = []
    _languages += [( 'cpp', 'C++11 (gcc 4.8.5)' )]
    _languages += [( 'cpp14' , 'C++14 (gcc 6.2.0)' )]
    _languages += [( 'c', 'C (gcc 4.8.5)' )]
    _languages += [( 'java8', 'Java8 (openjdk 1.8.0_111)' )]
    _languages += [( 'csharp', 'C# (mono 4.6.1)' )]
    _languages += [( 'perl', 'Perl (5.16.3)' )]
    _languages += [( 'perl6', 'Perl6 (rakudo 2016.10-114-g8e79509)' )]
    _languages += [( 'php', 'PHP (5.4.16)' )]
    _languages += [( 'python', 'Python2 (2.7.11)' )]
    _languages += [( 'python3', 'Python3 (3.5.1)' )]
    _languages += [( 'pypy2', 'PyPy2 (4.0.0)' )]
    _languages += [( 'pypy3', 'PyPy3 (2.4.0)' )]
    _languages += [( 'ruby', 'Ruby (2.3.1p112)' )]
    _languages += [( 'd', 'D (dmd 2.071.1)' )]
    _languages += [( 'go', 'Go (1.7.3)' )]
    _languages += [( 'haskell', 'Haskell (7.8.3)' )]
    _languages += [( 'scala', 'Scala (2.11.8)' )]
    _languages += [( 'nim', 'Nim (0.15.2)' )]
    _languages += [( 'rust', 'Rust (1.12.1)' )]
    _languages += [( 'kotlin', 'Kotlin (1.0.2)' )]
    _languages += [( 'scheme', 'Scheme (Gauche-0.9.4)' )]
    _languages += [( 'crystal', 'Crystal (0.19.4)' )]
    _languages += [( 'ocaml', 'OCaml (4.01.1)' )]
    _languages += [( 'fsharp', 'F# (4.0)' )]
    _languages += [( 'elixir', 'Elixir (0.12.5)' )]
    _languages += [( 'lua', 'Lua (LuaJit 2.0.4)' )]
    _languages += [( 'fortran', 'Fortran (gFortran 4.8.5)' )]
    _languages += [( 'node', 'JavaScript (node v7.0.0)' )]
    _languages += [( 'vim', 'Vim script (v8.0.0124)' )]
    _languages += [( 'sh', 'Bash (Bash 4.2.46)' )]
    _languages += [( 'text', 'Text (cat 8.22)' )]
    _languages += [( 'nasm', 'Assembler (nasm 2.10.07)' )]
    _languages += [( 'bf', 'Brainfuck (BFI 1.1)' )]
    _languages += [( 'Whitespace', 'Whitespace (0.3)' )]
    def get_languages(self):
        return list(map(lambda l: l[0], self.__class__._languages))
    def get_language_description(self, s):
        return dict(self.__class__._languages)[s]

    def submit(self, code, language=None, session=None):
        assert language in self.get_languages()
        # get
        url = self.get_url() + '/submit'
        log.status('GET: %s', url)
        resp = session.get(url)
        log.status(utils.describe_status_code(resp.status_code))
        resp.raise_for_status()
        # post
        soup = bs4.BeautifulSoup(resp.content.decode(resp.encoding), utils.html_parser)
        form = soup.find('form', action=re.compile(r'/submit$'))
        if not form:
            log.error('form not found')
            log.info('Did you logged in?')
            return False
        log.debug('form: %s', str(form))
        form = utils.FormSender(form, url=resp.url)
        form.set('source', code)
        form.set('lang', language)
        resp = form.request(session=session)
        resp.raise_for_status()
        # result
        if re.match(r'^https?://yukicoder\.me/submissions/[0-9]+/?$', resp.url):
            log.success('success: result: %s', resp.url)
            return True
        else:
            log.failure('failure')
            return False

    def get_service(self):
        return YukicoderService()


onlinejudge.dispatch.services += [ YukicoderService ]
onlinejudge.dispatch.problems += [ YukicoderProblem ]
