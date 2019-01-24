import unittest

import os
import subprocess
import sys

class ContinuousIntegrationTest(unittest.TestCase):
    '''A dummy test to run the commands same to CI on local environments
    '''

    def test_isort(self):
        if 'CI' not in os.environ:
            subprocess.check_call('isort --check-only --diff oj onlinejudge/**/*.py', shell=True, stdout=sys.stdout, stderr=sys.stderr)

    def test_yapf(self):
        if 'CI' not in os.environ:
            subprocess.check_call('yapf --diff oj onlinejudge/**/*.py | tee yapf.patch && test ! -s yapf.patch', shell=True, stdout=sys.stdout, stderr=sys.stderr)

    def test_mypy(self):
        if 'CI' not in os.environ:
            subprocess.check_call('mypy oj onlinejudge/**/*.py', shell=True, stdout=sys.stdout, stderr=sys.stderr)
