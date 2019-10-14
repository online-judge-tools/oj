import unittest

from onlinejudge import dispatch, service


class DispatchTest(unittest.TestCase):
    def test_problem_from_url(self):
        problem = dispatch.problem_from_url('https://atcoder.jp/contests/arc001/tasks/arc001_1')
        self.assertTrue(isinstance(problem, service.atcoder.AtCoderProblem))
        self.assertEqual(problem.get_url(), 'https://atcoder.jp/contests/arc001/tasks/arc001_1')
        self.assertEqual(problem.get_url(lang="ja"), 'https://atcoder.jp/contests/arc001/tasks/arc001_1?lang=ja')
        self.assertTrue(isinstance(problem.get_service(), service.atcoder.AtCoderService))
