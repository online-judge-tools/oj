# Python Version: 3.x
import contextlib
import datetime
import functools
import os
import pathlib
import platform
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import webbrowser
from logging import getLogger
from typing import *
from typing.io import *

import colorama
import onlinejudge_command.__about__ as version
import requests

import onlinejudge.utils as utils
from onlinejudge.type import *

logger = getLogger(__name__)

user_data_dir = utils.user_data_dir
user_cache_dir = utils.user_cache_dir
default_cookie_path = utils.default_cookie_path


@contextlib.contextmanager
def new_session_with_our_user_agent(*, path: pathlib.Path) -> Iterator[requests.Session]:
    session = requests.Session()
    session.headers['User-Agent'] = '{}/{} (+{})'.format(version.__package_name__, version.__version__, version.__url__)
    logger.debug('User-Agent: %s', session.headers['User-Agent'])
    with utils.with_cookiejar(session, path=path) as session:
        yield session


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

        # We need kill processes called from the "time" command using process groups. Without this, orphans spawn. see https://github.com/kmyk/online-judge-tools/issues/640
        preexec_fn = None
        if gnu_time is not None and os.name == 'posix':
            preexec_fn = os.setsid

        try:
            proc = subprocess.Popen(command, stdin=stdin, stdout=subprocess.PIPE, stderr=sys.stderr, preexec_fn=preexec_fn)
        except FileNotFoundError:
            logger.error('No such file or directory: %s', command)
            sys.exit(1)
        except PermissionError:
            logger.error('Permission denied: %s', command)
            sys.exit(1)
        answer = None  # type: Optional[bytes]
        try:
            answer, _ = proc.communicate(input=input, timeout=timeout)
        except subprocess.TimeoutExpired:
            pass
        finally:
            if preexec_fn is not None:
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                except ProcessLookupError:
                    pass
            else:
                proc.terminate()

        end = time.perf_counter()
        memory = None  # type: Optional[float]
        if gnu_time is not None:
            with open(fh.name) as fh1:
                reported = fh1.read()
            logger.debug('GNU time says:\n%s', reported)
            if reported.strip() and reported.splitlines()[-1].isdigit():
                memory = int(reported.splitlines()[-1]) / 1000
    info = {
        'answer': answer,  # Optional[byte]
        'elapsed': end - begin,  # float, in second
        'memory': memory,  # Optional[float], in megabyte
    }
    return info, proc


# These strings can control logging output.
NO_HEADER = 'NO_HEADER: '
HINT = 'HINT: '
SUCCESS = 'SUCCESS: '
FAILURE = 'FAILURE: '


def green(s: str) -> str:
    """green(s) color s with green.

    This function exists to encapsulate the coloring methods only in utils.py.
    """

    return colorama.Fore.GREEN + s + colorama.Fore.RESET


def red(s: str) -> str:
    """red(s) color s with red.

    This function exists to encapsulate the coloring methods only in utils.py.
    """

    return colorama.Fore.RED + s + colorama.Fore.RESET


def green_diff(s: str) -> str:
    """green_diff(s) is deprecated.
    """

    return colorama.Fore.RESET + colorama.Back.GREEN + colorama.Style.BRIGHT + s + colorama.Style.NORMAL + colorama.Back.RESET + colorama.Fore.GREEN


def red_diff(s: str) -> str:
    """red_diff(s) is deprecated.
    """

    return colorama.Fore.RESET + colorama.Back.RED + colorama.Style.BRIGHT + s + colorama.Style.NORMAL + colorama.Back.RESET + colorama.Fore.RED


def success(msg: str) -> str:
    """success(msg) adds a header to msg for logging.
    """

    return colorama.Fore.GREEN + 'SUCCESS' + colorama.Style.RESET + ': ' + msg


def failure(msg: str) -> str:
    """success(msg) adds a header to msg for logging.
    """

    return colorama.Fore.RED + 'FAILURE' + colorama.Style.RESET + ': ' + msg


def remove_suffix(s: str, suffix: str) -> str:
    assert s.endswith(suffix)
    return s[:-len(suffix)]


tzinfo_jst = datetime.timezone(datetime.timedelta(hours=+9), 'JST')

_PRETTY_BODY = 'BODY'
_PRETTY_WHITESPACE = 'WHITESPACE'
_PRETTY_NEWLINE = 'NEWLINE'
_PRETTY_HINT = 'HINT'


def _make_pretty_large_file_content(content: bytes, limit: int, head: int, tail: int) -> List[Tuple[str, str]]:
    """`_make_pretty_large_file_content` is an internal helper function.

    This function constructs only the intermediate representations. They have no color infomation.
    """

    assert head + tail < limit

    char_in_line, _ = shutil.get_terminal_size()
    char_in_line = max(char_in_line, 40)  # shutil.get_terminal_size() may return too small values (e.g. (0, 0) on Circle CI) successfully (i.e. fallback is not used). see https://github.com/kmyk/online-judge-tools/pull/611

    def from_line(line: str) -> List[Tuple[str, str]]:
        body = line.rstrip()
        newline = line[len(body):]
        tokens = []
        tokens.append((_PRETTY_BODY, body))
        if newline:
            if newline in ('\n', '\r\n'):
                tokens.append((_PRETTY_NEWLINE, newline))
            else:
                whitespace = newline.rstrip('\n')
                newline = newline[len(whitespace):]
                if whitespace:
                    tokens.append((_PRETTY_WHITESPACE, whitespace))
                tokens.append((_PRETTY_HINT, '(trailing whitespace)'))
                if newline:
                    tokens.append((_PRETTY_NEWLINE, newline))
        return tokens

    def candidate_do_nothing(text: str) -> List[Tuple[str, str]]:
        tokens = []
        for line in text.splitlines(keepends=True):
            tokens += from_line(line)
        return tokens

    def candidate_line_based(text: str) -> List[Tuple[str, str]]:
        lines = text.splitlines(keepends=True)
        if len(lines) < limit:
            return candidate_do_nothing(text)

        tokens = []
        for line in lines[:head]:
            tokens += from_line(line)
        tokens.append((_PRETTY_HINT, '... ({} lines) ...\n'.format(len(lines[head:-tail]))))
        for line in lines[-tail:]:
            tokens += from_line(line)
        return tokens

    def candidate_char_based(text: str) -> List[Tuple[str, str]]:
        if len(text) < char_in_line * limit:
            return candidate_do_nothing(text)

        l = len(text[:char_in_line * head].rstrip())
        r = len(text) - char_in_line * tail
        tokens = []
        for line in text[:l].splitlines(keepends=True):
            tokens += from_line(line)
        tokens.append((_PRETTY_HINT, '... ({} chars) ...'.format(r - l)))
        for line in text[r:].splitlines(keepends=True):
            tokens += from_line(line)
        return tokens

    def count_size(tokens: Iterable[Tuple[str, str]]) -> int:
        size = 0
        for _, s in tokens:
            size += len(s)
        return size

    if not content:
        return [(_PRETTY_HINT, '(empty)')]

    tokens = []
    try:
        text = content.decode()
    except UnicodeDecodeError as e:
        tokens.append((_PRETTY_HINT, str(e)))
        text = content.decode(errors='replace')

    candidates = [
        candidate_do_nothing(text),
        candidate_line_based(text),
        candidate_char_based(text),
    ]  # type: List[List[Tuple[str, str]]]
    tokens.extend(min(candidates, key=count_size))

    assert len(tokens) >= 1
    if tokens[-1][0] == _PRETTY_BODY:
        tokens.append((_PRETTY_HINT, '(no trailing newline)'))
    if not text.rstrip('\n'):
        tokens.append((_PRETTY_HINT, '(only newline)'))

    return tokens


def make_pretty_large_file_content(content: bytes, limit: int, head: int, tail: int, bold: bool = False) -> str:
    font_dim = lambda s: colorama.Style.DIM + s + colorama.Style.RESET_ALL
    font_bold = lambda s: colorama.Style.BRIGHT + s + colorama.Style.RESET_ALL

    tokens = _make_pretty_large_file_content(content=content, limit=limit, head=head, tail=tail)
    result = []
    for key, value in tokens:
        if key == _PRETTY_BODY:
            if bold:
                value = font_bold(value)
        elif key == _PRETTY_WHITESPACE:
            value = font_dim(value.replace(' ', '_').replace('\t', '\\t').replace('\r', '\\r'))
        elif key == _PRETTY_NEWLINE:
            value = font_dim(value.replace('\r', '\\r'))
        elif key == _PRETTY_HINT:
            value = font_dim(value)
        else:
            assert False
        result.append(value)
    return ''.join(result)


def is_windows_subsystem_for_linux() -> bool:
    return platform.uname().system == 'Linux' and 'Microsoft' in platform.uname().release


@functools.lru_cache(maxsize=None)
def webbrowser_register_explorer_exe() -> None:
    """webbrowser_register_explorer registers `explorer.exe` in the list of browsers under Windows Subsystem for Linux.

    See https://github.com/online-judge-tools/oj/issues/773
    """

    # There is an issue that the terminal is cleared after `.open_new_tab()`. The reason is unknown, but adding an argurment `preferred=True` to `webbrowser.register` resolves this issues.

    # See https://github.com/online-judge-tools/oj/pull/784

    if not is_windows_subsystem_for_linux():
        return
    instance = webbrowser.GenericBrowser('explorer.exe')
    webbrowser.register('explorer', None, instance)  # TODO: use `preferred=True` to solve the issue that terminal is cleared, when the version of Python becomes 3.7 or higher
