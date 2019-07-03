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


def run(args, *, env=None, check=False):
    env = env or dict(os.environ)
    env['PYTHONPATH'] = str(pathlib.Path(__file__).parent.parent)  # this is required to run in sandboxes
    return subprocess.run([sys.executable, '-m', 'onlinejudge._implementation.main'] + args, stdout=subprocess.PIPE, stderr=sys.stderr, env=env, check=check)


def run_in_sandbox(args, files):
    with sandbox(files) as tempdir:
        proc = run(args)
        return {
            'proc': proc,
            'tempdir': tempdir,
        }
