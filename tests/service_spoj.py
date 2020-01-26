import unittest

from onlinejudge.service.spoj import SPOJProblem, SPOJService
from onlinejudge.type import TestCase


class CodeChefSerivceTest(unittest.TestCase):
    def test_from_url(self):
        self.assertIsInstance(SPOJService.from_url('https://www.spoj.com/'), SPOJService)
        self.assertIsNone(SPOJService.from_url('https://www.facebook.com/'))


class CodeChefProblemTest(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(SPOJProblem.from_url('https://www.spoj.com/problems/ACARGO/').problem_id, 'ACARGO')

    def test_download_samples(self):
        self.assertEqual(SPOJProblem.from_url('https://www.spoj.com/problems/ACARGO/').download_sample_cases(), [
            TestCase(name='sample-1', input_name='Sample Input:', input_data=b'3 5\n0\n1\n3\n2 3\n0\n1\n5 20\n2\n7\n12\n9\n13\n0 0\n', output_name='Sample Output:', output_data=b'1\n0\n10\n'),
        ])

    def test_download_samples_todo(self):
        # No samples found.
        self.assertFalse(SPOJProblem.from_url('https://www.spoj.com/problems/MKLABELS/').download_sample_cases())
