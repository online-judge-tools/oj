import unittest

import tests.utils
from onlinejudge.service.atcoder import AtCoderService
from onlinejudge.service.codeforces import CodeforcesService
from onlinejudge.service.hackerrank import HackerRankService
from onlinejudge.service.toph import TophService
from onlinejudge.service.yukicoder import YukicoderService


# TODO: add tests for login without `--check` opiton. Copy credentials used in tests https://github.com/online-judge-tools/api-client and write tests.
class LoginCheckTest(unittest.TestCase):
    def snippet_call_login_check_failure(self, url):
        with tests.utils.sandbox(files=[]) as _:
            path = 'cookie.jar'  # use dummy cookie to check in an empty state
            proc = tests.utils.run(['--cookie', path, 'login', '--check', url])
            self.assertEqual(proc.returncode, 1)

    def snippet_call_login_check_success(self, url):
        tests.utils.run(['login', '--check', url], check=True)

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

    @unittest.skipIf(not tests.utils.is_logged_in(AtCoderService()), 'login is required')
    def test_call_login_check_atcoder_success(self):
        self.snippet_call_login_check_success('https://atcoder.jp/')

    @unittest.skipIf(not tests.utils.is_logged_in(CodeforcesService()), 'login is required')
    def test_call_login_check_codeforces_success(self):
        self.snippet_call_login_check_success('https://codeforces.com/')

    @unittest.skipIf(not tests.utils.is_logged_in(HackerRankService()), 'login is required')
    def test_call_login_check_hackerrank_success(self):
        self.snippet_call_login_check_success('https://www.hackerrank.com/')

    @unittest.skipIf(not tests.utils.is_logged_in(TophService()), 'login is required')
    def test_call_login_check_toph_success(self):
        self.snippet_call_login_check_success('https://toph.co/')

    @unittest.skipIf(not tests.utils.is_logged_in(YukicoderService()), 'login is required')
    def test_call_login_check_yukicoder_success(self):
        self.snippet_call_login_check_success('https://yukicoder.me/')
