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
        contest = AtCoderContest.from_url('https://atcoder.jp/contests/agc028')
        problems = contest.list_problems()
        self.assertEqual(len(problems), 7)
        self.assertEqual(problems[0].get_alphabet(), 'A')
        self.assertEqual(problems[0].get_task_name(), 'Two Abbreviations')
        self.assertEqual(problems[0].get_time_limit_msec(), 2000)
        self.assertEqual(problems[0].get_memory_limit_byte(), 1024 * 1000 * 1000)
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

    def test_load_details(self):
        problem = AtCoderProblem.from_url('https://atcoder.jp/contests/abc118/tasks/abc118_a')
        self.assertEqual(problem.get_alphabet(), 'A')
        self.assertEqual(problem.get_task_name(), 'B +/- A')
        self.assertEqual(problem.get_time_limit_msec(), 2000)
        self.assertEqual(problem.get_memory_limit_byte(), 1024 * 1000 * 1000)
        self.assertEqual(problem.get_score(), 100)

    def test_get_alphabet(self):
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/agc028/tasks/agc028_f').get_alphabet(), 'F')
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/agc028/tasks/agc028_f2').get_alphabet(), 'F2')

    def test_get_score(self):
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/future-contest-2018-final/tasks/future_contest_2018_final_a').get_score(), 50000000)
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/abc001/tasks/abc001_4').get_score(), None)


class AtCoderSubmissionTest(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(AtCoderSubmission.from_url('https://atcoder.jp/contests/kupc2012/submissions/2097011').contest_id, 'kupc2012')
        self.assertEqual(AtCoderSubmission.from_url('https://atcoder.jp/contests/kupc2012/submissions/2097011').submission_id, 2097011)
        self.assertEqual(AtCoderSubmission.from_url('https://qupc2014.contest.atcoder.jp/submissions/1444440').contest_id, 'qupc2014')
        self.assertEqual(AtCoderSubmission.from_url('https://qupc2014.contest.atcoder.jp/submissions/1444440').submission_id, 1444440)

    def test_submission_info(self):
        submission = AtCoderSubmission.from_url('https://atcoder.jp/contests/agc030/submissions/3904911')
        self.assertEqual(submission.get_submission_time().year, 2018)
        self.assertEqual(submission.get_submission_time().month, 12)
        self.assertEqual(submission.get_submission_time().day, 31)
        self.assertEqual(submission.get_user_id(), 'kimiyuki')
        self.assertEqual(submission.get_problem().problem_id, 'agc030_b')
        self.assertEqual(submission.get_language_name(), 'C++14 (GCC 5.4.1)')
        self.assertEqual(submission.get_score(), 800)
        self.assertEqual(submission.get_code_size(), 1457)
        self.assertEqual(submission.get_exec_time_msec(), 85)
        self.assertEqual(submission.get_memory_byte(), 3328 * 1000)

    def test_get_test_sets(self):
        submission = AtCoderSubmission.from_url('https://atcoder.jp/contests/arc028/submissions/223928')
        test_cases = submission.get_test_sets()
        self.assertEqual(len(test_cases), 3)
        self.assertEqual(test_cases[0].set_name, 'Sample')
        self.assertEqual(test_cases[0].score, 0)
        self.assertEqual(test_cases[0].max_score, 0)
        self.assertEqual(test_cases[0].test_case_names, ['sample_01.txt', 'sample_02.txt'])
        self.assertEqual(test_cases[1].set_name, 'Subtask1')
        self.assertEqual(test_cases[1].score, 40)
        self.assertEqual(test_cases[1].max_score, 40)
        self.assertEqual(len(test_cases[1].test_case_names), 13)
        self.assertEqual(test_cases[2].set_name, 'Subtask2')
        self.assertEqual(test_cases[2].score, 0)
        self.assertEqual(test_cases[2].max_score, 60)
        self.assertEqual(len(test_cases[2].test_case_names), 20)

    def test_get_test_cases(self):
        submission = AtCoderSubmission.from_url('https://atcoder.jp/contests/tricky/submissions/119944')
        test_cases = submission.get_test_cases()
        self.assertEqual(len(test_cases), 2)
        self.assertEqual(test_cases[0].case_name, 'input_01.txt')
        self.assertEqual(test_cases[0].status, 'TLE')
        self.assertEqual(test_cases[0].exec_time_msec, None)
        self.assertEqual(test_cases[0].memory_byte, None)
        self.assertEqual(test_cases[1].case_name, 'input_02.txt')
        self.assertEqual(test_cases[1].status, 'AC')
        self.assertEqual(test_cases[1].exec_time_msec, 131)
        self.assertEqual(test_cases[1].memory_byte, 7400 * 1000)

    def test_get_source_code(self):
        submission = AtCoderSubmission.from_url('https://atcoder.jp/contests/abc100/submissions/3082514')
        self.assertEqual(submission.get_source_code(), b'/9\\|\\B/c:(\ncYay!')
        self.assertEqual(submission.get_code_size(), 16)

        submission = AtCoderSubmission.from_url('https://atcoder.jp/contests/abc100/submissions/4069980')
        self.assertEqual(submission.get_source_code(), b'/9\\|\\B/c:(\r\ncYay!')
        self.assertEqual(submission.get_code_size(), 17)

        submission = AtCoderSubmission.from_url('https://atcoder.jp/contests/abc100/submissions/4317534')
        self.assertEqual(submission.get_source_code(), b'/9\\|\\B/c:(\r\ncYay!\r\n')
        self.assertEqual(submission.get_code_size(), 19)


if __name__ == '__main__':
    unittest.main()
