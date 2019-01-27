import os
import subprocess
import sys
import unittest

# TODO: these command should be written at once, at only .travis.yml or at only here

paths = ['oj', 'onlinejudge', 'setup.py', 'tests']


class ContinuousIntegrationTest(unittest.TestCase):
    """A dummy test to run the commands same to CI on local environments"""

    def test_isort(self):
        if 'CI' not in os.environ:
            subprocess.check_call(['isort', '--check-only', '--diff', '--recursive'] + paths, stdout=sys.stdout, stderr=sys.stderr)

    def test_yapf(self):
        if 'CI' not in os.environ:
            output = subprocess.check_output(['yapf', '--diff', '--recursive'] + paths, stderr=sys.stderr)
            self.assertEqual(output, b'')

    def test_mypy(self):
        if 'CI' not in os.environ:
            subprocess.check_call(['mypy', '--show-traceback'] + paths, stdout=sys.stdout, stderr=sys.stderr)
