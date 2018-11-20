# Python Version: 3.x
# -*- coding: utf-8 -*-
import onlinejudge.implementation.logging as log
import onlinejudge.implementation.version as version
from onlinejudge.problem import LabeledString, TestCase
import re
import os
import os.path
import requests
import bs4
import contextlib
import urllib.parse
import http.cookiejar
import http.client
import subprocess
import posixpath
import sys
import ast
import time
from typing import *
from typing.io import *

default_data_dir = os.path.join(os.environ.get('XDG_DATA_HOME') or os.path.expanduser('~/.local/share'), 'onlinejudge')
html_parser = 'lxml'

def parcentformat(s: str, table: Dict[str, str]) -> str:
    assert '%' not in table or table['%'] == '%'
    table['%'] = '%'
    result = ''
    for m in re.finditer('[^%]|%(.)', s):
        if m.group(1):
            if m.group(1) in table:
                result += table[m.group(1)]
        else:
            result += m.group(0)
    return result

def describe_status_code(status_code: int) -> str:
    return '{} {}'.format(status_code, http.client.responses[status_code])

def previous_sibling_tag(tag: bs4.Tag) -> bs4.Tag:
    tag = tag.previous_sibling
    while tag and not isinstance(tag, bs4.Tag):
        tag = tag.previous_sibling
    return tag

def next_sibling_tag(tag: bs4.Tag) -> bs4.Tag:
    tag = tag.next_sibling
    while tag and not isinstance(tag, bs4.Tag):
        tag = tag.next_sibling
    return tag

def new_default_session() -> requests.Session:  # without setting cookiejar
    session = requests.Session()
    session.headers['User-Agent'] += ' (+{})'.format(version.__url__)
    return session

default_cookie_path = os.path.join(default_data_dir, 'cookie.jar')

@contextlib.contextmanager
def with_cookiejar(session: requests.Session, path: str) -> Generator[requests.Session, None, None]:
    path = path or default_cookie_path
    session.cookies = http.cookiejar.LWPCookieJar(path)  # type: ignore
    if os.path.exists(path):
        log.status('load cookie from: %s', path)
        session.cookies.load()  # type: ignore
    yield session
    log.status('save cookie to: %s', path)
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    session.cookies.save()  # type: ignore
    os.chmod(path, 0o600)  # NOTE: to make secure a little bit


class SampleZipper(object):
    def __init__(self):
        self.data = []
        self.dangling = None

    def add(self, s: str, name: str = '') -> None:
        if self.dangling is None:
            if re.search('output', name, re.IGNORECASE) or re.search('出力', name):
                log.warning('strange name for input string: %s', name)
            self.dangling = LabeledString(name, s)
        else:
            if re.search('input', name, re.IGNORECASE) or re.search('入力', name):
                if not (re.search('output', name, re.IGNORECASE) or re.search('出力', name)):  # to ignore titles like "Output for Sample Input 1"
                    log.warning('strange name for output string: %s', name)
            self.data += [ TestCase(self.dangling, LabeledString(name, s)) ]
            self.dangling = None

    def get(self) -> List[TestCase]:
        if self.dangling is not None:
            log.error('dangling sample string: %s', self.dangling[1])
        return self.data

class FormSender(object):
    def __init__(self, form: bs4.Tag, url: str):
        assert isinstance(form, bs4.Tag)
        assert form.name == 'form'
        self.form = form
        self.url = url
        self.payload: Dict[str, str] = {}
        self.files: Dict[str, IO[Any]] = {}
        for input in self.form.find_all('input'):
            log.debug('input: %s', str(input))
            if input.attrs.get('type') in [ 'checkbox', 'radio' ]:
                continue
            if 'name' in input.attrs and 'value' in input.attrs:
                self.payload[input['name']] = input['value']

    def set(self, key: str, value: str) -> None:
        self.payload[key] = value

    def get(self) -> Dict[str, str]:
        return self.payload

    def set_file(self, key: str, value: IO[Any]) -> None:
        self.files[key] = value

    def request(self, session: requests.Session, action: Optional[str] = None, **kwargs) -> requests.Response:
        action = action or self.form['action']
        url = urllib.parse.urljoin(self.url, action)
        method = self.form['method'].upper()
        log.status('%s: %s', method, url)
        log.debug('payload: %s', str(self.payload))
        resp = session.request(method, url, data=self.payload, files=self.files, **kwargs)
        log.status(describe_status_code(resp.status_code))
        return resp

def dos2unix(s: str) -> str:
    return s.replace('\r\n', '\n')
def textfile(s: str) -> str:  # should have trailing newline
    if s.endswith('\n'):
        return s
    elif '\r\n' in s:
        return s + '\r\n'
    else:
        return s + '\n'

# http://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons-in-python/12850496#12850496
def singleton(cls):
    instance = cls()
    # Always return the same object
    cls.__new__ = staticmethod(lambda cls: instance)
    # Disable __init__
    try:
        del cls.__init__
    except AttributeError:
        pass
    return cls

def exec_command(command: List[str], timeout: float = None, **kwargs) -> Tuple[bytes, subprocess.Popen]:
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=sys.stderr, **kwargs)
    except FileNotFoundError:
        log.error('No such file or directory: %s', command)
        sys.exit(1)
    except PermissionError:
        log.error('Permission denied: %s', command)
        sys.exit(1)
    try:
        answer, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        answer = b''
    return answer, proc

# We should use this instead of posixpath.normpath
# posixpath.normpath doesn't collapse a leading duplicated slashes. see: https://stackoverflow.com/questions/7816818/why-doesnt-os-normpath-collapse-a-leading-double-slash
def normpath(path: str) -> str:
    path = posixpath.normpath(path)
    if path.startswith('//'):
        path = '/' + path.lstrip('/')
    return path


def request(method: str, url: str, session: requests.Session, raise_for_status: bool = True, **kwargs) -> requests.Response:
    assert method in [ 'GET', 'POST' ]
    kwargs.setdefault('allow_redirects', True)
    log.status('%s: %s', method, url)
    resp = session.request(method, url, **kwargs)
    log.status(describe_status_code(resp.status_code))
    if raise_for_status:
        resp.raise_for_status()
    return resp
