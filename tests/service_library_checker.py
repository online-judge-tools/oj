import unittest

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

    def test_download_samples(self):
        self.assertEqual(LibraryCheckerProblem.from_url('https://judge.yosupo.jp/problem/unionfind').download_sample_cases(), [
            TestCase(name='example_00', input_name='example_00.in', input_data=b'4 7\n1 0 1\n0 0 1\n0 2 3\n1 0 1\n1 1 2\n0 0 2\n1 1 3\n', output_name='example_00.out', output_data=b'0\n1\n0\n1\n'),
        ])
