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

    def test_from_url_mx(self):
        self.assertEqual(CodeforcesContest.from_url('http://m1.codeforces.com/contest/1333').get_url(), CodeforcesContest.from_url('https://codeforces.com/contest/1333').get_url())
        self.assertEqual(CodeforcesContest.from_url('http://m2.codeforces.com/contest/1333').get_url(), CodeforcesContest.from_url('https://codeforces.com/contest/1333').get_url())
        self.assertEqual(CodeforcesContest.from_url('http://m3.codeforces.com/contest/1333').get_url(), CodeforcesContest.from_url('https://codeforces.com/contest/1333').get_url())
        self.assertIsNone(CodeforcesContest.from_url('http://m4.codeforces.com/contest/1333'))

    def test_list_problems_data(self):
        contest = CodeforcesContest.from_url('https://codeforces.com/contest/1157')
        problems = contest.list_problem_data()
        self.assertEqual(len(problems), 8)
        self.assertEqual(problems[0].name, 'Reachable Numbers')
        self.assertEqual(problems[1].problem.index, 'B')
        self.assertEqual(problems[2].name, 'Increasing Subsequence (easy version)')
        self.assertEqual(problems[3].problem.index, 'C2')
        self.assertEqual(problems[4].name, 'N Problems During K Days')
        self.assertEqual(problems[5].problem.index, 'E')
        self.assertEqual(problems[6].tags, ['constructive algorithms', 'dp', 'greedy', 'two pointers'])
        self.assertEqual(problems[7].tags, ['brute force', 'constructive algorithms'])

    def test_list_problems(self):
        contest = CodeforcesContest.from_url('https://codeforces.com/contest/1157')
        problems = contest.list_problems()
        self.assertEqual(len(problems), 8)
        self.assertEqual(problems[0].get_url(), 'https://codeforces.com/contest/1157/problem/A')
        self.assertEqual(problems[6].get_url(), 'https://codeforces.com/contest/1157/problem/F')
        self.assertEqual(problems[7].download_data().tags, ['brute force', 'constructive algorithms'])

    def test_download_data(self):
        contest = CodeforcesContest.from_url('http://codeforces.com/contest/1200')
        data = contest.download_data()
        self.assertEqual(data.duration_seconds, 7200)
        self.assertEqual(data.frozen, False)
        self.assertEqual(data.name, 'Codeforces Round #578 (Div. 2)')
        self.assertEqual(data.phase, 'FINISHED')
        self.assertEqual(data.start_time_seconds, 1565526900)
        self.assertEqual(data.type, 'CF')


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
        data = problem.download_data()
        self.assertEqual(data.name, 'Almost All')
        self.assertEqual(data.points, 2000)
        self.assertEqual(data.rating, 2800)
        self.assertEqual(data.tags, ['constructive algorithms', 'trees'])
        self.assertEqual(data.type, 'PROGRAMMING')
