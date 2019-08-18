# -*- coding: utf-8 -*-
import unittest

from onlinejudge.service.codeforces import CodeforcesContest, CodeforcesProblem, CodeforcesService


class CodeforcesSerivceTest(unittest.TestCase):
    def test_from_url(self):
        self.assertIsInstance(CodeforcesService.from_url('http://codeforces.com/'), CodeforcesService)
        self.assertIsInstance(CodeforcesService.from_url('https://codeforces.com/'), CodeforcesService)
        self.assertIsInstance(CodeforcesService.from_url('https://codeforces.com/problemset/problem/700/B'), CodeforcesService)
        self.assertIsNone(CodeforcesService.from_url('https://atcoder.jp/'))


class CodeforcesContestTest(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(CodeforcesContest.from_url('http://codeforces.com/contest/542').contest_id, 542)
        self.assertEqual(CodeforcesContest.from_url('http://codeforces.com/gym/101025').contest_id, 101025)
        self.assertIsNone(CodeforcesContest.from_url('https://atcoder.jp/contests/abc120'))

    def test_list_problems(self):
        contest = CodeforcesContest.from_url('https://codeforces.com/contest/1157')
        problems = contest.list_problem_contents()
        self.assertEqual(len(problems), 8)
        self.assertEqual(problems[0].name, 'Reachable Numbers')
        self.assertEqual(problems[1].problem.index, 'B')
        self.assertEqual(problems[2].name, 'Increasing Subsequence (easy version)')
        self.assertEqual(problems[3].problem.index, 'C2')
        self.assertEqual(problems[4].name, 'N Problems During K Days')
        self.assertEqual(problems[5].problem.index, 'E')
        self.assertEqual(problems[6].tags, ['constructive algorithms', 'dp', 'greedy', 'two pointers'])
        self.assertEqual(problems[7].tags, ['brute force', 'constructive algorithms'])

    def test_download_content(self):
        contest = CodeforcesContest.from_url('http://codeforces.com/contest/1200')
        content = contest.download_content()
        self.assertEqual(content.duration_seconds, 7200)
        self.assertEqual(content.frozen, False)
        self.assertEqual(content.name, 'Codeforces Round #578 (Div. 2)')
        self.assertEqual(content.phase, 'FINISHED')
        self.assertEqual(content.start_time_seconds, 1565526900)
        self.assertEqual(content.type, 'CF')


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
        self.assertIsNone(CodeforcesProblem.from_url('https://atcoder.jp/contests/abc120/tasks/abc120_c'))

    def test_from_url_corner_cases(self):
        # 0
        self.assertEqual(CodeforcesProblem.from_url('https://codeforces.com/contest/1105/problem/0').index, 'A')
        self.assertEqual(CodeforcesProblem.from_url('https://codeforces.com/contest/1105/problem/1'), None)

        # lower case
        self.assertEqual(CodeforcesProblem.from_url('https://codeforces.com/contest/1110/problem/H').index, 'H')
        self.assertEqual(CodeforcesProblem.from_url('https://codeforces.com/contest/1110/problem/h').index, 'H')

        # F2
        self.assertEqual(CodeforcesProblem.from_url('https://codeforces.com/contest/1133/problem/E').index, 'E')
        self.assertEqual(CodeforcesProblem.from_url('https://codeforces.com/contest/1133/problem/F1').index, 'F1')
        self.assertEqual(CodeforcesProblem.from_url('https://codeforces.com/contest/1133/problem/F2').index, 'F2')

    def test_download_problem(self):
        problem = CodeforcesProblem.from_url('http://codeforces.com/contest/1205/problem/D')
        content = problem.download_content()
        self.assertEqual(content.name, 'Almost All')
        self.assertEqual(content.points, 2000)
        self.assertEqual(content.rating, 2800)
        self.assertEqual(content.tags, ['constructive algorithms', 'trees'])
        self.assertEqual(content.type, 'PROGRAMMING')
