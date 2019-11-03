import unittest

from onlinejudge.dispatch import problem_from_url, service_from_url, submission_from_url
from onlinejudge.type import Problem, Service, Submission


class TypeTest(unittest.TestCase):
    def test_instantiate_abstract_class(self):
        self.assertRaises(TypeError, Service)
        self.assertRaises(TypeError, Problem)
        self.assertRaises(TypeError, Submission)

    def test_service_eq(self):
        self.assertEqual(service_from_url('https://atcoder.jp/'), service_from_url('https://atcoder.jp/contests/agc030'))
        self.assertNotEqual(service_from_url('https://atcoder.jp/'), service_from_url('https://codeforces.com/'))

    def test_problem_eq(self):
        self.assertEqual(problem_from_url('https://codeforces.com/contest/1244/problem/C'), problem_from_url('https://codeforces.com/contest/1244/problem/C'))
        self.assertNotEqual(problem_from_url('https://codeforces.com/contest/1244/problem/C'), problem_from_url('https://codeforces.com/contest/1244/problem/B'))
        self.assertNotEqual(problem_from_url('https://codeforces.com/contest/1244/problem/C'), problem_from_url('https://atcoder.jp/contests/abc143/tasks/abc143_c'))

    def test_submission_eq(self):
        self.assertEqual(submission_from_url('https://atcoder.jp/contests/abc143/submissions/8264863'), submission_from_url('https://atcoder.jp/contests/abc143/submissions/8264863'))
        self.assertNotEqual(submission_from_url('https://atcoder.jp/contests/abc143/submissions/8264863'), submission_from_url('https://atcoder.jp/contests/abc143/submissions/8264897'))
