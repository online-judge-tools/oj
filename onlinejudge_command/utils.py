# Python Version: 3.x
import contextlib
import datetime
import functools
import os
import pathlib
import platform
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import webbrowser
from typing import *
from typing.io import *

import onlinejudge_command.__about__ as version
import onlinejudge_command.logging as log
import requests

import onlinejudge.utils as utils
from onlinejudge.type import *

user_data_dir = utils.user_data_dir
user_cache_dir = utils.user_cache_dir
default_cookie_path = utils.default_cookie_path


@contextlib.contextmanager
def new_session_with_our_user_agent(*, path: pathlib.Path) -> Iterator[requests.Session]:
    session = requests.Session()
    session.headers['User-Agent'] = '{}/{} (+{})'.format(version.__package_name__, version.__version__, version.__url__)
    log.debug('User-Agent: %s', session.headers['User-Agent'])
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
            log.error('No such file or directory: %s', command)
            sys.exit(1)
        except PermissionError:
            log.error('Permission denied: %s', command)
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
            log.debug('GNU time says:\n%s', reported)
            if reported.strip() and reported.splitlines()[-1].isdigit():
                memory = int(reported.splitlines()[-1]) / 1000
    info = {
        'answer': answer,  # Optional[byte]
        'elapsed': end - begin,  # float, in second
        'memory': memory,  # Optional[float], in megabyte
    }
    return info, proc


def remove_suffix(s: str, suffix: str) -> str:
    assert s.endswith(suffix)
    return s[:-len(suffix)]


tzinfo_jst = datetime.timezone(datetime.timedelta(hours=+9), 'JST')


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
