# Python Version: 3.x
import contextlib
import datetime
import distutils.version
import functools
import http.client
import http.cookiejar
import json
import pathlib
import posixpath
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
from typing import *
from typing.io import *

import appdirs
import bs4
import requests

import onlinejudge.__about__ as version
import onlinejudge._implementation.logging as log
from onlinejudge.type import *

config_dir = pathlib.Path(appdirs.user_config_dir(version.__package_name__))
data_dir = pathlib.Path(appdirs.user_data_dir(version.__package_name__))
cache_dir = pathlib.Path(appdirs.user_cache_dir(version.__package_name__))
html_parser = 'lxml'


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


def new_session_with_our_user_agent() -> requests.Session:
    session = requests.Session()
    session.headers['User-Agent'] += ' (+{})'.format(version.__url__)
    return session


_default_session = None  # Optional[requests.Session]


def get_default_session() -> requests.Session:
    """
    :note: cookie is not saved to disk
    """
    global _default_session
    if _default_session is None:
        _default_session = new_session_with_our_user_agent()
    return _default_session


default_cookie_path = data_dir / 'cookie.jar'


@contextlib.contextmanager
def with_cookiejar(session: requests.Session, path: pathlib.Path = default_cookie_path) -> Generator[requests.Session, None, None]:
    session.cookies = http.cookiejar.LWPCookieJar(str(path))  # type: ignore
    if path.exists():
        log.status('load cookie from: %s', path)
        session.cookies.load()  # type: ignore
    yield session
    log.status('save cookie to: %s', path)
    path.parent.mkdir(parents=True, exist_ok=True)
    session.cookies.save()  # type: ignore
    path.chmod(0o600)  # NOTE: to make secure a little bit


class FormSender(object):
    def __init__(self, form: bs4.Tag, url: str):
        assert isinstance(form, bs4.Tag)
        assert form.name == 'form'
        self.form = form
        self.url = url
        self.payload = {}  # type: Dict[str, str]
        self.files = {}  # type: Dict[str, IO[Any]]
        for input in self.form.find_all('input'):
            log.debug('input: %s', str(input))
            if input.attrs.get('type') in ['checkbox', 'radio']:
                continue
            if 'name' in input.attrs and 'value' in input.attrs:
                self.payload[input['name']] = input['value']

    def set(self, key: str, value: str) -> None:
        self.payload[key] = value

    def get(self) -> Dict[str, str]:
        return self.payload

    def set_file(self, key: str, filename: str, content: bytes) -> None:
        self.files[key] = (filename, content)  # type: ignore

    def unset(self, key: str) -> None:
        del self.payload[key]

    def request(self, session: requests.Session, method: str = None, action: Optional[str] = None, raise_for_status: bool = True, **kwargs) -> requests.Response:
        if method is None:
            method = self.form['method'].upper()
        url = urllib.parse.urljoin(self.url, action)
        action = action or self.form['action']
        log.debug('payload: %s', str(self.payload))
        return request(method, url, session=session, raise_for_status=raise_for_status, data=self.payload, files=self.files, **kwargs)


def dos2unix(s: str) -> str:
    return s.replace('\r\n', '\n')


def textfile(s: str) -> str:  # should have trailing newline
    if s.endswith('\n'):
        return s
    elif '\r\n' in s:
        return s + '\r\n'
    else:
        return s + '\n'


def exec_command(command: List[str], timeout: Optional[float] = None, **kwargs) -> Tuple[bytes, subprocess.Popen]:
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
    assert method in ['GET', 'POST']
    kwargs.setdefault('allow_redirects', True)
    log.status('%s: %s', method, url)
    if 'data' in kwargs:
        log.debug('data: %s', repr(kwargs['data']))
    resp = session.request(method, url, **kwargs)
    if resp.url != url:
        log.status('redirected: %s', resp.url)
    log.status(describe_status_code(resp.status_code))
    if raise_for_status:
        resp.raise_for_status()
    return resp


def get_latest_version_from_pypi() -> str:
    pypi_url = 'https://pypi.org/pypi/{}/json'.format(version.__package_name__)
    version_cache_path = cache_dir / "pypi.json"
    update_interval = 60 * 60 * 8  # 8 hours

    # load cache
    if version_cache_path.exists():
        with version_cache_path.open() as fh:
            cache = json.load(fh)
        if time.time() < cache['time'] + update_interval:
            return cache['version']

    # get
    try:
        resp = request('GET', pypi_url, session=requests.Session())
        data = json.loads(resp.content.decode())
        value = data['info']['version']
    except requests.RequestException as e:
        log.error(str(e))
        value = '0.0.0'  # ignore since this failure is not important
    cache = {
        'time': int(time.time()),  # use timestamp because Python's standard datetime library is too weak to parse strings
        'version': value,
    }

    # store cache
    version_cache_path.parent.mkdir(parents=True, exist_ok=True)
    with version_cache_path.open('w') as fh:
        json.dump(cache, fh)

    return value


def is_update_available_on_pypi() -> bool:
    a = distutils.version.StrictVersion(version.__version__)
    b = distutils.version.StrictVersion(get_latest_version_from_pypi())
    return a < b


def remove_prefix(s: str, prefix: str) -> str:
    assert s.startswith(prefix)
    return s[len(prefix):]


def remove_suffix(s: str, suffix: str) -> str:
    assert s.endswith(suffix)
    return s[:-len(suffix)]


tzinfo_jst = datetime.timezone(datetime.timedelta(hours=+9), 'JST')


def getter_with_load_details(name: str, type: Union[str, type]) -> Callable:
    """
    :note: confirm that the type annotation `get_foo = getter_with_load_details("_foo", type=int)  # type: Callable[..., int]` is correct one
    :note: this cannot be a decorator, since mypy fails to recognize the types

    This functions is bad one, but I think

        get_foo = getter_with_load_details("_foo", type=int)  # type: Callable[..., int]

    is better than

        def get_foo(self, session: Optional[requests.Session] = None) -> int:
            if self._foo is None:
                self._load_details(session=session)
                assert self._foo is not None
            return self._foo

    Of course the latter is better when it is used only once, but the former is better when the pattern is repeated.
    """

    @functools.wraps(lambda self: getattr(self, name))
    def wrapper(self, session: Optional[requests.Session] = None):
        if getattr(self, name) is None:
            assert session is None or isinstance(session, requests.Session)
            self._load_details(session=session)
        return getattr(self, name)

    # add documents
    assert type is not None
    py_class = lambda s: ':py:class:`{}`'.format(s)
    if isinstance(type, str):
        if type.count('[') == 0:
            rst = py_class(type)
        elif type.count('[') == 1:
            a, b = remove_suffix(type, ']').split('[')
            rst = '{} [ {} ]'.format(py_class(a), py_class(b))
        else:
            assert False
    elif type in (int, float, str, bytes, datetime.datetime, datetime.timedelta):
        rst = py_class(type.__name__)
    else:
        assert False
    wrapper.__doc__ = ':return: {}'.format(rst)

    return wrapper


def snip_large_file_content(content: bytes, limit: int, head: int, tail: int, bold: bool = False) -> str:
    assert head + tail < limit
    try:
        text = content.decode()
    except UnicodeDecodeError as e:
        return str(e)
    font = log.bold if bold else (lambda s: s)
    char_in_line, _ = shutil.get_terminal_size()

    def snip_line_based():
        lines = text.splitlines(keepends=True)
        if len(lines) < limit:
            return font(text)
        else:
            return ''.join([
                font(''.join(lines[:head])),
                '... ({} lines) ...\n'.format(len(lines[head:-tail])),
                font(''.join(lines[-tail:])),
            ])

    def snip_char_based():
        if len(text) < char_in_line * limit:
            return font(text)
        else:
            return ''.join([
                font(text[:char_in_line * head]),
                '... ({} chars) ...'.format(len(text[char_in_line * head:-char_in_line * tail])),
                font(text[-char_in_line * tail:]),
            ])

    return min([font(text), snip_line_based(), snip_char_based()], key=len)


class DummySubmission(Submission):
    def __init__(self, url: str, problem: Problem):
        self.url = url
        self.problem = problem

    def download_code(self, session: Optional[requests.Session] = None) -> bytes:
        raise NotImplementedError

    def get_url(self) -> str:
        return self.url

    def get_problem(self) -> Problem:
        return self.problem

    def get_service(self) -> Service:
        raise NotImplementedError

    def __repr__(self) -> str:
        return '{}({}, problem={})'.format(self.__class__, self.url, self.problem)

    @classmethod
    def from_url(cls, s: str) -> Optional[Submission]:
        return None
