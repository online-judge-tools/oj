import os
import subprocess
import unittest

import tests.utils as utils

import onlinejudge.utils
from onlinejudge.service.library_checker import LibraryCheckerProblem, LibraryCheckerService
from onlinejudge.type import TestCase


class LibraryCheckerSerivceTest(unittest.TestCase):
    def test_from_url(self):
        self.assertIsInstance(LibraryCheckerService.from_url('https://judge.yosupo.jp/'), LibraryCheckerService)
        self.assertIsInstance(LibraryCheckerService.from_url('https://judge.yosupo.jp/problem/point_add_range_sum'), LibraryCheckerService)
        self.assertIsNone(LibraryCheckerService.from_url('https://www.facebook.com/'))


class LibraryCheckerProblemTest(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(LibraryCheckerProblem.from_url('https://judge.yosupo.jp/problem/point_add_range_sum').problem_id, 'point_add_range_sum')

    @unittest.skipIf(os.name == 'nt', "Library Checker is not supported on Windows")
    def test_download_samples(self):
        self.assertEqual(LibraryCheckerProblem.from_url('https://judge.yosupo.jp/problem/unionfind').download_sample_cases(), [
            TestCase(name='example_00', input_name='example_00.in', input_data=b'4 7\n1 0 1\n0 0 1\n0 2 3\n1 0 1\n1 1 2\n0 0 2\n1 1 3\n', output_name='example_00.out', output_data=b'0\n1\n0\n1\n'),
        ])

    @unittest.skipIf(os.name == 'nt', "Library Checker is not supported on Windows")
    def test_pull_repository(self):
        # reset
        LibraryCheckerService.is_repository_updated = False
        with utils.chdir(str(onlinejudge.utils.user_cache_dir / 'library-checker-problems')):
            # the first commit https://github.com/yosupo06/library-checker-problems/commit/fb33114329382695b1a17655843b490b04a08ab6
            subprocess.check_call(['git', 'reset', '--hard', 'fb33114329382695b1a17655843b490b04a08ab6'])

        # ensure that it automatically runs `$ git pull`
        self.assertEqual(LibraryCheckerProblem.from_url('https://judge.yosupo.jp/problem/aplusb').download_sample_cases(), [
            TestCase(name='example_00', input_name='example_00.in', input_data=b'1234 5678\n', output_name='example_00.out', output_data=b'6912\n'),
            TestCase(name='example_01', input_name='example_01.in', input_data=b'1000000000 1000000000\n', output_name='example_01.out', output_data=b'2000000000\n'),
        ])
