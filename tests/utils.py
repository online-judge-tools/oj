import contextlib
import os
import pathlib
import subprocess
import sys
import tempfile


@contextlib.contextmanager
def chdir(path):
    cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(cwd)


def prepare_files(files):
    for f in files:
        path = pathlib.Path(f['path'])
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(str(path), 'wb') as fh:
            fh.write(f['data'].encode())
        if f.get('executable', False):
            path.chmod(0o755)


@contextlib.contextmanager
def sandbox(files):
    with tempfile.TemporaryDirectory() as tempdir:
        tempdir = str(pathlib.Path(tempdir).resolve())  # to expand paths like "C:\PROGRA~1" on Windows
        with chdir(tempdir):
            prepare_files(files)
            yield tempdir


def get_oj_exe():
    oj_exe = os.environ.get('TEST_OJ_EXE')
    if oj_exe is not None:
        return [str(pathlib.Path(oj_exe).resolve())]
    else:
        return [sys.executable, '-m', 'onlinejudge._implementation.main']


def run(args, *, env=None, check=False, pipe_stderr=False, oj_exe=get_oj_exe()):
    # oj_exe should be evaluated out of sandboxes
    env = env or dict(os.environ)
    env['PYTHONPATH'] = str(pathlib.Path(__file__).parent.parent)  # this is required to run in sandboxes
    err = subprocess.PIPE if pipe_stderr else sys.stderr
    return subprocess.run(oj_exe + args, stdout=subprocess.PIPE, stderr=err, env=env, check=check)


def run_in_sandbox(args, files, pipe_stderr=False):
    with sandbox(files) as tempdir:
        proc = run(args, pipe_stderr=pipe_stderr)
        return {
            'proc': proc,
            'tempdir': tempdir,
        }


def cat():
    if os.name == 'nt':
        return '{} -c "import sys; sys.stdout.buffer.write(sys.stdin.buffer.read())"'.format(sys.executable)
    else:
        return 'cat'


def sleep_1sec():
    if os.name == 'nt':
        return '{} -c "import time; time.sleep(1)"'.format(sys.executable)
    else:
        return 'sleep 1.0'


def python_c(cmd):
    assert '"' not in cmd
    return '{} -c "{}"'.format(sys.executable, cmd)


def python_script(path):
    assert '"' not in path
    return '{} "{}"'.format(sys.executable, path)


def is_logged_in(service, memo={}):
    # functools.lru_cache is unusable since Service are unhashable
    url = service.get_url()
    if url not in memo:
        proc = run(['login', '--check', url])
        memo[url] = proc.returncode == 0
    return memo[url]
