import unittest

from onlinejudge.service.aoj import AOJProblem, AOJService


class AOJSerivceTest(unittest.TestCase):
    def test_from_url(self):
        self.assertIsInstance(AOJService.from_url('https://judge.u-aizu.ac.jp/onlinejudge/'), AOJService)
        self.assertIsInstance(AOJService.from_url('https://onlinejudge.u-aizu.ac.jp/home'), AOJService)
        self.assertIsNone(AOJService.from_url('https://atcoder.jp/'))


class AOJProblemTest(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(AOJProblem.from_url('https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=DSL_1_A').problem_id, 'DSL_1_A')
        self.assertEqual(AOJProblem.from_url('https://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=0100').problem_id, '0100')
        self.assertEqual(AOJProblem.from_url('http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=2256&lang=jp').problem_id, '2256')
        self.assertEqual(AOJProblem.from_url('https://onlinejudge.u-aizu.ac.jp/courses/library/3/DSL/3/DSL_3_B').problem_id, 'DSL_3_B')
        self.assertEqual(AOJProblem.from_url('https://onlinejudge.u-aizu.ac.jp/challenges/sources/JAG/Spring/2394?year=2011').problem_id, '2394')
