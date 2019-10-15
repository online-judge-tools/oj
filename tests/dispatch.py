import unittest

from onlinejudge import dispatch, service


class DispatchAtCoderTest(unittest.TestCase):
    def test_problem_from_url(self):
        problem = dispatch.problem_from_url('https://atcoder.jp/contests/arc001/tasks/arc001_1')
        self.assertTrue(isinstance(problem, service.atcoder.AtCoderProblem))
        self.assertEqual(problem.get_url(), 'https://atcoder.jp/contests/arc001/tasks/arc001_1')
        self.assertEqual(problem.get_url(lang='ja'), 'https://atcoder.jp/contests/arc001/tasks/arc001_1?lang=ja')
        self.assertTrue(isinstance(problem.get_service(), service.atcoder.AtCoderService))
        self.assertEqual(problem.download_input_format(), '\r\n<var>N</var>\r\n<var>c_1c_2c_3…c_N</var>\r\n')
        self.assertEqual(problem.get_name(), 'センター採点')

    def test_submission_from_url(self):
        submission = dispatch.submission_from_url('https://atcoder.jp/contests/agc039/submissions/7874055')
        self.assertTrue(isinstance(submission, service.atcoder.AtCoderSubmission))
        self.assertTrue(isinstance(submission.get_service(), service.atcoder.AtCoderService))
        with self.assertRaises(Exception):
            submission.get_problem()
        problem = submission.download_problem()
        self.assertEqual(problem.contest_id, "agc039")
        self.assertEqual(problem.problem_id, "agc039_b")

    def test_contest_from_url(self):
        contest = dispatch.contest_from_url('https://atcoder.jp/contests/agc030')
        self.assertTrue(isinstance(contest, service.atcoder.AtCoderContest))
        self.assertTrue(isinstance(contest.get_service(), service.atcoder.AtCoderService))

    def test_service_from_url(self):
        service1 = dispatch.service_from_url('https://atcoder.jp/')
        self.assertTrue(isinstance(service1, service.atcoder.AtCoderService))
        self.assertEqual(service1.get_url_of_login_page(), 'https://atcoder.jp/login')
        self.assertEqual(service1.get_user_history_url(22), 'https://atcoder.jp/users/22/history/json')


class DispatchCodeForcesTest(unittest.TestCase):
    def test_problem_from_url(self):
        problem = dispatch.problem_from_url('https://codeforces.com/contest/1244/problem/C')
        self.assertTrue(isinstance(problem, service.codeforces.CodeforcesProblem))
        self.assertTrue(isinstance(problem.get_service(), service.codeforces.CodeforcesService))

    def test_contest_from_url(self):
        contest = dispatch.contest_from_url('https://codeforces.com/contest/1244')
        self.assertTrue(isinstance(contest, service.codeforces.CodeforcesContest))
        self.assertTrue(isinstance(contest.get_service(), service.codeforces.CodeforcesService))

    def test_service_from_url(self):
        service1 = dispatch.service_from_url('https://codeforces.com/')
        self.assertTrue(isinstance(service1, service.codeforces.CodeforcesService))
        self.assertEqual(service1.get_url_of_login_page(), 'https://codeforces.com/enter')


class InvalidDispatchTest(unittest.TestCase):
    def test_problem_from_url(self):
        self.assertIsNone(dispatch.problem_from_url('https://atcoder.jp/contests/agc039'))

    def test_submission_from_url(self):
        self.assertIsNone(dispatch.submission_from_url('https://atcoder.jp/contests/agc039'))

    def test_contest_from_url(self):
        self.assertIsNone(dispatch.contest_from_url('https://atcoder.jp/'))

    def test_service_from_url(self):
        self.assertIsNone(dispatch.service_from_url('https://www.yahoo.co.jp/'))
