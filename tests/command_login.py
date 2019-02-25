import os
import subprocess
import sys
import time
import unittest

import tests.utils


class LoginTest(unittest.TestCase):
    def snippet_call_login_check_failure(self, url):
        ojtools = os.path.abspath('oj')
        with tests.utils.sandbox(files=[]) as tempdir:
            env = dict(**os.environ)
            env['HOME'] = tempdir
            self.assertRaises
            proc = subprocess.run([ojtools, 'login', '--check', url], env=env, stdout=sys.stdout, stderr=sys.stderr)
            self.assertEqual(proc.returncode, 1)

    def test_call_login_check_atcoder_failure(self):
        self.snippet_call_login_check_failure('https://atcoder.jp/')

    def test_call_login_check_codeforces_failure(self):
        self.snippet_call_login_check_failure('https://codeforces.com/')

    def test_call_login_check_hackerrank_failure(self):
        self.snippet_call_login_check_failure('https://www.hackerrank.com/')

    def test_call_login_check_toph_failure(self):
        self.snippet_call_login_check_failure('https://toph.co/')

    def test_call_login_check_yukicoder_failure(self):
        self.snippet_call_login_check_failure('https://yukicoder.me/')

    @unittest.skipIf('CI' in os.environ, 'login is required')
    def test_call_login_check_atcoder_success(self):
        ojtools = os.path.abspath('oj')
        subprocess.check_call([ojtools, 'login', '--check', 'https://atcoder.jp/'], stdout=sys.stdout, stderr=sys.stderr)

    @unittest.skipIf('CI' in os.environ, 'login is required')
    def test_call_login_check_codeforces_success(self):
        ojtools = os.path.abspath('oj')
        subprocess.check_call([ojtools, 'login', '--check', 'https://codeforces.com/'], stdout=sys.stdout, stderr=sys.stderr)

    @unittest.skipIf('CI' in os.environ, 'login is required')
    def test_call_login_check_hackerrank_success(self):
        ojtools = os.path.abspath('oj')
        subprocess.check_call([ojtools, 'login', '--check', 'https://www.hackerrank.com/'], stdout=sys.stdout, stderr=sys.stderr)

    @unittest.skipIf('CI' in os.environ, 'login is required')
    def test_call_login_check_toph_success(self):
        ojtools = os.path.abspath('oj')
        subprocess.check_call([ojtools, 'login', '--check', 'https://toph.co/'], stdout=sys.stdout, stderr=sys.stderr)

    @unittest.skipIf('CI' in os.environ, 'login is required')
    def test_call_login_check_yukicoder_success(self):
        ojtools = os.path.abspath('oj')
        subprocess.check_call([ojtools, 'login', '--check', 'https://yukicoder.me/'], stdout=sys.stdout, stderr=sys.stderr)
