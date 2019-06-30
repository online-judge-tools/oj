import inspect
import unittest

from onlinejudge.service.facebook import FacebookHackerCupProblem, FacebookHackerCupService
from onlinejudge.type import TestCase


class FacebookHackerCupSerivceTest(unittest.TestCase):
    def test_from_url(self):
        self.assertIsInstance(FacebookHackerCupService.from_url('https://www.facebook.com/hackercup/'), FacebookHackerCupService)
        self.assertIsInstance(FacebookHackerCupService.from_url('https://www.facebook.com/hackercup/problem/448364075989193/'), FacebookHackerCupService)
        self.assertIsNone(FacebookHackerCupService.from_url('https://www.facebook.com/AtCoder/'))


class FacebookHackerCupProblemTest(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(FacebookHackerCupProblem.from_url('https://www.facebook.com/hackercup/problem/448364075989193/').problem_id, 448364075989193)

    def test_download_samples(self):
        problem = FacebookHackerCupProblem.from_url('https://www.facebook.com/hackercup/problem/2390352741015547/')
        sample_input = (inspect.cleandoc("""
            6
            2 2 2
            6 3 0 0 0 10
            2 4 0 0 0 10
            2 2 1
            6 3 0 0 0 10
            2 4 0 0 0 10
            2 0 1
            6 3 0 0 0 10
            2 4 0 0 0 10
            4 1 3
            1 1 1 0 0 2
            1 2 1 0 1 2
            10 7 5
            15 19 34 41 32 44
            34 3 25 2 17 38
            10000 6011 4543
            434894347 263348046 2565 3970 1267 622277910
            524251054 294718567 0 1 3718 689139248
            """) + '\n').encode()
        sample_output = (inspect.cleandoc("""
            Case #1: 4
            Case #2: 5
            Case #3: -1
            Case #4: 3
            Case #5: 45
            Case #6: 766791757
            """) + '\n').encode()
        self.assertEqual(problem.download_sample_cases(), [
            TestCase(
                'sample',
                'connect_the_dots_sample_input.txt',
                sample_input,
                'connect_the_dots_sample_output.txt',
                sample_output,
            ),
        ])
