# -*- coding: utf-8 -*-
import unittest

from onlinejudge.service.atcoder import AtCoderContest, AtCoderProblem, AtCoderService, AtCoderSubmission


class AtCoderSerivceTest(unittest.TestCase):
    def test_from_url(self):
        service = AtCoderService()
        self.assertEqual(AtCoderService.from_url('https://atcoder.jp/'), service)
        self.assertEqual(AtCoderService.from_url('https://beta.atcoder.jp/'), service)
        self.assertEqual(AtCoderService.from_url('https://abc001.contest.atcoder.jp/'), service)
        self.assertEqual(AtCoderService.from_url('https://atcoder.jp/contests/agc001/submissions/806160'), service)
        self.assertEqual(AtCoderService.from_url('https://codeforces.com/'), None)

    def test_iterate_contests(self):
        contests = list(AtCoderService().iterate_contests())
        contest_ids = [contest.contest_id for contest in contests]
        self.assertIn('arc001', contest_ids)
        self.assertIn('abc100', contest_ids)
        self.assertIn('kupc2012', contest_ids)
        contest, = [contest for contest in contests if contest.contest_id == 'utpc2013']
        self.assertEqual(contest.get_start_time().year, 2014)
        self.assertEqual(contest.get_start_time().month, 3)
        self.assertEqual(contest.get_start_time().day, 2)
        self.assertEqual(contest.get_contest_name(), '東京大学プログラミングコンテスト2013')
        self.assertEqual(contest.get_duration().total_seconds(), 5 * 60 * 60)
        self.assertEqual(contest.get_rated_range(), 'All')


class AtCoderContestTest(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(AtCoderContest.from_url('https://kupc2014.contest.atcoder.jp/tasks/kupc2014_d').contest_id, 'kupc2014')
        self.assertEqual(AtCoderContest.from_url('https://atcoder.jp/contests/agc030').contest_id, 'agc030')
        self.assertEqual(AtCoderContest.from_url('https://atcoder.jp/contests/'), None)

    def test_list_problems(self):
        contest = AtCoderContest('agc028')
        problems = contest.list_problems()
        self.assertEqual(len(problems), 7)
        self.assertEqual(problems[0].get_alphabet(), 'A')
        self.assertEqual(problems[0].get_task_name(), 'Two Abbreviations')
        self.assertEqual(problems[0].get_time_limit_msec(), 2000)
        self.assertEqual(problems[0].get_memory_limit_mb(), 1024)
        self.assertEqual(problems[5].get_alphabet(), 'F')
        self.assertEqual(problems[5].problem_id, 'agc028_f')
        self.assertEqual(problems[6].get_alphabet(), 'F2')
        self.assertEqual(problems[6].problem_id, 'agc028_f2')


class AtCoderProblemTest(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(AtCoderProblem.from_url('https://kupc2014.contest.atcoder.jp/tasks/kupc2014_d').contest_id, 'kupc2014')
        self.assertEqual(AtCoderProblem.from_url('https://kupc2014.contest.atcoder.jp/tasks/kupc2014_d').problem_id, 'kupc2014_d')
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/agc030/tasks/agc030_c').contest_id, 'agc030')
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/agc030/tasks/agc030_c').problem_id, 'agc030_c')


class AtCoderSubmissionTest(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(AtCoderSubmission.from_url('https://atcoder.jp/contests/kupc2012/submissions/2097011').contest_id, 'kupc2012')
        self.assertEqual(AtCoderSubmission.from_url('https://atcoder.jp/contests/kupc2012/submissions/2097011').submission_id, 2097011)
        self.assertEqual(AtCoderSubmission.from_url('https://qupc2014.contest.atcoder.jp/submissions/1444440').contest_id, 'qupc2014')
        self.assertEqual(AtCoderSubmission.from_url('https://qupc2014.contest.atcoder.jp/submissions/1444440').submission_id, 1444440)


if __name__ == '__main__':
    unittest.main()
