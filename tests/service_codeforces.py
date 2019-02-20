# -*- coding: utf-8 -*-
import unittest

from onlinejudge.service.codeforces import CodeforcesProblem, CodeforcesService


class CodeforcesSerivceTest(unittest.TestCase):
    def test_from_url(self):
        service = CodeforcesService()
        self.assertEqual(CodeforcesService.from_url('http://codeforces.com/'), service)
        self.assertEqual(CodeforcesService.from_url('https://codeforces.com/'), service)
        self.assertEqual(CodeforcesService.from_url('https://codeforces.com/problemset/problem/700/B'), service)
        self.assertEqual(CodeforcesService.from_url('https://atcoder.jp/'), None)


class CodeforcesProblemTest(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(CodeforcesProblem.from_url('http://codeforces.com/problemset/problem/700/B').contest_id, 700)
        self.assertEqual(CodeforcesProblem.from_url('http://codeforces.com/problemset/problem/700/B').index, 'B')
        self.assertEqual(CodeforcesProblem.from_url('http://codeforces.com/contest/538/problem/H').contest_id, 538)
        self.assertEqual(CodeforcesProblem.from_url('http://codeforces.com/contest/538/problem/H').index, 'H')
        self.assertEqual(CodeforcesProblem.from_url('http://codeforces.com/gym/101021/problem/A').contest_id, 101021)
        self.assertEqual(CodeforcesProblem.from_url('http://codeforces.com/gym/101021/problem/A').index, 'A')
        self.assertEqual(CodeforcesProblem.from_url('https://codeforces.com/contest/1080/problem/A').contest_id, 1080)
        self.assertEqual(CodeforcesProblem.from_url('https://codeforces.com/contest/1080/problem/A').index, 'A')
