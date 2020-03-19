# Python Version: 3.x
import contextlib
import datetime
import distutils.version
import functools
import http.client
import http.cookiejar
import json
import os
import posixpath
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.parse
from typing import *
from typing.io import *

import bs4

import onlinejudge.__about__ as version
import onlinejudge.utils
from onlinejudge.type import *
from onlinejudge.utils import *  # re-export

new_session_with_our_user_agent = onlinejudge.utils._new_session_with_our_user_agent
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


# remove all HTML tag without interpretation (except <br>)
# remove all comment
# using DFS(Depth First Search)
# discussed in https://github.com/kmyk/online-judge-tools/issues/553
def parse_content(parent: Union[bs4.NavigableString, bs4.Tag, bs4.Comment]) -> bs4.NavigableString:
    res = ''
    if isinstance(parent, bs4.Comment):
        pass
    elif isinstance(parent, bs4.NavigableString):
        return parent
    else:
        children = parent.contents
        if len(children) == 0:
            html_tag = str(parent)
            return bs4.NavigableString('\n') if 'br' in html_tag else bs4.NavigableString('')
        else:
            for child in children:
                res += parse_content(child)
    return bs4.NavigableString(res)


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


def exec_command(command_str: str, *, stdin: Optional[IO[Any]] = None, input: Optional[bytes] = None, timeout: Optional[float] = None, gnu_time: Optional[str] = None) -> Tuple[Dict[str, Any], subprocess.Popen]:
    if input is not None:
        assert stdin is None
        stdin = subprocess.PIPE  # type: ignore
    if gnu_time is not None:
        context = tempfile.NamedTemporaryFile(delete=True)  # type: Any
    else:
        context = contextlib.ExitStack()  # TODO: we should use contextlib.nullcontext() if possible
    with context as fh:
        command = shlex.split(command_str)
        if gnu_time is not None:
            command = [gnu_time, '-f', '%M', '-o', fh.name, '--'] + command
        if os.name == 'nt':
            # HACK: without this encoding and decoding, something randomly fails with multithreading; see https://github.com/kmyk/online-judge-tools/issues/468
            command = command_str.encode().decode()  # type: ignore
        begin = time.perf_counter()

        # We need kill processes called from the "time" command using process groups. Without this, zombies spawn. see https://github.com/kmyk/online-judge-tools/issues/640
        preexec_fn = None
        if gnu_time is not None and os.name == 'posix':
            preexec_fn = os.setsid

        try:
            proc = subprocess.Popen(command, stdin=stdin, stdout=subprocess.PIPE, stderr=sys.stderr, preexec_fn=preexec_fn)
        except FileNotFoundError:
            log.error('No such file or directory: %s', command)
            sys.exit(1)
        except PermissionError:
            log.error('Permission denied: %s', command)
            sys.exit(1)
        answer = None  # type: Optional[bytes]
        try:
            answer, _ = proc.communicate(input=input, timeout=timeout)
        except subprocess.TimeoutExpired:
            if preexec_fn is not None:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            else:
                proc.terminate()

        end = time.perf_counter()
        memory = None  # type: Optional[float]
        if gnu_time is not None:
            with open(fh.name) as fh1:
                reported = fh1.read()
            log.debug('GNU time says:\n%s', reported)
            if reported.strip() and reported.splitlines()[-1].isdigit():
                memory = int(reported.splitlines()[-1]) / 1000
    info = {
        'answer': answer,  # Optional[byte]
        'elapsed': end - begin,  # float, in second
        'memory': memory,  # Optional[float], in megabyte
    }
    return info, proc


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
    version_cache_path = user_cache_dir / "pypi.json"
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


def make_pretty_large_file_content(content: bytes, limit: int, head: int, tail: int, bold: bool = False) -> str:
    assert head + tail < limit
    try:
        text = content.decode()
    except UnicodeDecodeError as e:
        return str(e)

    def font(line: str) -> str:
        if not line.endswith('\n'):
            line += log.dim('(no trailing newline)')
        else:

            def repl(m):
                if m.group(1) == '\r':
                    return log.dim('\\r' + m.group(2))
                else:
                    return log.dim(m.group(1).replace(' ', '_').replace('\t', '\\t').replace('\r', '\\r') + '(trailing spaces)' + m.group(2))

            line = re.sub(r'(\s+)(\n)$', repl, line)
        if bold:
            line = log.bold(line)
        return line

    char_in_line, _ = shutil.get_terminal_size()
    char_in_line = max(char_in_line, 40)  # shutil.get_terminal_size() may return too small values (e.g. (0, 0) on Circle CI) successfully (i.e. fallback is not used). see https://github.com/kmyk/online-judge-tools/pull/611

    def no_snip_text() -> List[str]:
        lines = text.splitlines(keepends=True)
        return [''.join(map(font, lines))]

    def snip_line_based() -> List[str]:
        lines = text.splitlines(keepends=True)
        if len(lines) < limit:
            return []
        return [''.join([
            *map(font, lines[:head]),
            '... ({} lines) ...\n'.format(len(lines[head:-tail])),
            *map(font, lines[-tail:]),
        ])]

    def snip_char_based() -> List[str]:
        if len(text) < char_in_line * limit:
            return []
        return [''.join([
            *map(font, text[:char_in_line * head].splitlines(keepends=True)),
            '... ({} chars) ...'.format(len(text[char_in_line * head:-char_in_line * tail])),
            *map(font, text[-char_in_line * tail:].splitlines(keepends=True)),
        ])]

    candidates = []  # type: List[str]
    candidates += no_snip_text()
    candidates += snip_line_based()
    candidates += snip_char_based()
    return min(candidates, key=len)


class DummySubmission(Submission):
    def __init__(self, url: str, problem: Problem):
        self.url = url
        self.problem = problem

    def download_code(self, session: Optional[requests.Session] = None) -> bytes:
        raise NotImplementedError

    def get_url(self) -> str:
        return self.url

    def download_problem(self, *, session: Optional[requests.Session] = None) -> Problem:
        raise NotImplementedError

    def get_service(self) -> Service:
        raise NotImplementedError

    def __repr__(self) -> str:
        return '{}({}, problem={})'.format(self.__class__, self.url, self.problem)

    @classmethod
    def from_url(cls, s: str) -> Optional[Submission]:
        return None
