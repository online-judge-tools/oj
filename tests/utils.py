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
        with open(str(path), 'w') as fh:
            fh.write(f['data'])
        if f.get('executable', False):
            path.chmod(0o755)


@contextlib.contextmanager
def sandbox(files):
    with tempfile.TemporaryDirectory() as tempdir:
        with chdir(tempdir):
            prepare_files(files)
            yield tempdir


def get_oj_exe():
    oj_exe = os.environ.get('TEST_OJ_EXE')
    if oj_exe is not None:
        return [str(pathlib.Path(oj_exe).resolve())]
    else:
        return [sys.executable, '-m', 'onlinejudge._implementation.main']


def run(args, *, env=None, check=False, oj_exe=get_oj_exe()):
    # oj_exe should be evaluated out of sandboxes
    env = env or dict(os.environ)
    env['PYTHONPATH'] = str(pathlib.Path(__file__).parent.parent)  # this is required to run in sandboxes
    return subprocess.run(oj_exe + args, stdout=subprocess.PIPE, stderr=sys.stderr, env=env, check=check)


def run_in_sandbox(args, files):
    with sandbox(files) as tempdir:
        proc = run(args)
        return {
            'proc': proc,
            'tempdir': tempdir,
        }


def cat():
    if os.name == 'nt':
        return '{} -c "import sys; sys.stdout.write(sys.stdin.read())"'.format(sys.executable)
    else:
        return 'cat'


def python_c(cmd):
    assert '"' not in cmd
    return '{} -c "{}"'.format(sys.executable, cmd)
