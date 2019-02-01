import os
import subprocess
import sys
import unittest

# TODO: these command should be written at once, at only .travis.yml or at only here

paths = ['oj', 'onlinejudge', 'setup.py', 'tests']


class ContinuousIntegrationTest(unittest.TestCase):
    """A dummy test to run the commands same to CI on local environments"""

    @unittest.skipIf('CI' in os.environ, 'the same command is call from .travis.yml')
    def test_isort(self):
        subprocess.check_call(['isort', '--check-only', '--diff', '--recursive'] + paths, stdout=sys.stdout, stderr=sys.stderr)

    @unittest.skipIf('CI' in os.environ, 'the same command is call from .travis.yml')
    def test_yapf(self):
        output = subprocess.check_output(['yapf', '--diff', '--recursive'] + paths, stderr=sys.stderr)
        self.assertEqual(output, b'')

    @unittest.skipIf('CI' in os.environ, 'the same command is call from .travis.yml')
    def test_mypy(self):
        subprocess.check_call(['mypy', '--show-traceback'] + paths, stdout=sys.stdout, stderr=sys.stderr)
