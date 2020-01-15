import unittest

from onlinejudge.service.codechef import CodeChefProblem, CodeChefService
from onlinejudge.type import SampleParseError, TestCase


class CodeChefSerivceTest(unittest.TestCase):
    def test_from_url(self):
        self.assertIsInstance(CodeChefService.from_url('https://www.codechef.com/'), CodeChefService)
        self.assertIsNone(CodeChefService.from_url('https://www.facebook.com/'))


class CodeChefProblemTest(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(CodeChefProblem.from_url('https://www.codechef.com/COOK113A/problems/DAND').contest_id, 'COOK113A')
        self.assertEqual(CodeChefProblem.from_url('https://www.codechef.com/COOK113A/problems/DAND').problem_id, 'DAND')

    def test_download_samples(self):
        self.assertEqual(CodeChefProblem.from_url('https://www.codechef.com/COOK113A/problems/DAND').download_sample_cases(), [
            TestCase(name='sample', input_name='Example Input', input_data=b'6\n1 9 3\n4 7 1\n10 75 12\n3 8 3\n5 10 2\n192 913893 3812\n', output_name='Example Output', output_data=b'4\n7\n64\n4\n8\n909312\n'),
        ])
        self.assertEqual(CodeChefProblem.from_url('https://www.codechef.com/PLIN2020/problems/CNTSET').download_sample_cases(), [
            TestCase(name='sample', input_name='Sample Input', input_data=b'4 2\n', output_name='Sample Output', output_data=b'12\n'),
        ])

    def test_download_samples_todo(self):
        self.assertRaises(SampleParseError, lambda: CodeChefProblem.from_url('https://www.codechef.com/CNES2017/problems/ACESQN').download_sample_cases())
