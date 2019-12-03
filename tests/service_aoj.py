import unittest

from onlinejudge.service.aoj import AOJArenaProblem, AOJProblem, AOJService
from onlinejudge.type import TestCase


class AOJSerivceTest(unittest.TestCase):
    def test_from_url(self):
        self.assertIsInstance(AOJService.from_url('http://judge.u-aizu.ac.jp/onlinejudge/'), AOJService)
        self.assertIsInstance(AOJService.from_url('https://onlinejudge.u-aizu.ac.jp/home'), AOJService)
        self.assertIsNone(AOJService.from_url('https://atcoder.jp/'))


class AOJProblemTest(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(AOJProblem.from_url('http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=DSL_1_A').problem_id, 'DSL_1_A')
        self.assertEqual(AOJProblem.from_url('http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=0100').problem_id, '0100')
        self.assertEqual(AOJProblem.from_url('http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=2256&lang=jp').problem_id, '2256')
        self.assertEqual(AOJProblem.from_url('https://onlinejudge.u-aizu.ac.jp/courses/library/3/DSL/3/DSL_3_B').problem_id, 'DSL_3_B')
        self.assertEqual(AOJProblem.from_url('https://onlinejudge.u-aizu.ac.jp/challenges/sources/JAG/Spring/2394?year=2011').problem_id, '2394')
        self.assertIsNone(AOJProblem.from_url('https://onlinejudge.u-aizu.ac.jp/services/room.html#RitsCamp19Day2/problems/A'))

    def test_download_sample_cases(self):
        self.assertEqual(AOJProblem.from_url('http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=DSL_1_A').download_sample_cases(), [
            TestCase(name='sample-1', input_name='1', input_data=b'5 12\n0 1 4\n0 2 3\n1 1 2\n1 3 4\n1 1 4\n1 3 2\n0 1 3\n1 2 4\n1 3 0\n0 0 4\n1 0 2\n1 3 0\n', output_name='1', output_data=b'0\n0\n1\n1\n1\n0\n1\n1\n'),
        ])
        self.assertEqual(AOJProblem.from_url('http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=0100').download_sample_cases(), [
            TestCase(name='sample-1', input_name='1', input_data=b'4\n1001 2000 520\n1002 1800 450\n1003 1600 625\n1001 200 1220\n2\n1001 100 3\n1005 1000 100\n2\n2013 5000 100\n2013 5000 100\n0\n', output_name='1', output_data=b'1001\n1003\nNA\n2013\n'),
        ])
        self.assertEqual(AOJProblem.from_url('http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=2256&lang=jp').download_sample_cases(), [
            TestCase(name='sample-1', input_name='1', input_data=b'2 2 1\n0 1\n2 1\n3 3 1\n1 1\n2 1\n0 0 0\n', output_name='1', output_data=b'0.5000000000\n0.1666666667\n'),
        ])
        self.assertEqual(AOJProblem.from_url('https://onlinejudge.u-aizu.ac.jp/courses/library/3/DSL/3/DSL_3_B').download_sample_cases(), [
            TestCase(name='sample-1', input_name='1', input_data=b'6 2\n4 1 2 1 3 5\n', output_name='1', output_data=b'2\n'),
            TestCase(name='sample-2', input_name='2', input_data=b'6 3\n4 1 2 1 3 5\n', output_name='2', output_data=b'3\n'),
            TestCase(name='sample-3', input_name='3', input_data=b'3 4\n1 2 3\n', output_name='3', output_data=b'0\n'),
        ])
        self.assertEqual(AOJProblem.from_url('https://onlinejudge.u-aizu.ac.jp/challenges/sources/JAG/Spring/2394?year=2011').download_sample_cases(), [
            TestCase(name='sample-1', input_name='1', input_data=b'4\n0 0\n10 0\n10 10\n0 10\n3\n0 0\n1 0\n0 1\n0\n', output_name='1', output_data=b'Case 1: 14.142135624\nCase 2: 1.41421356\n'),
        ])

    def test_download_sample_cases_not_registered(self):
        # see: https://github.com/kmyk/online-judge-tools/issues/207
        self.assertEqual(AOJProblem.from_url('https://onlinejudge.u-aizu.ac.jp/challenges/sources/ICPC/Regional/1399').download_sample_cases(), [
            TestCase(name='sample-1', input_name='Sample Input 1', input_data=b'5\n1 2 3 4 5\n1 2 3 4 5\n', output_name=' Sample Output 1', output_data=b'2 3 4 5 1\n'),
            TestCase(name='sample-2', input_name='Sample Input 2', input_data=b'5\n3 4 5 6 7\n1 3 5 7 9\n', output_name='Sample Output 2', output_data=b'9 5 7 3 1\n'),
            TestCase(name='sample-3', input_name='Sample Input 3', input_data=b'5\n3 2 2 1 1\n1 1 2 2 3\n', output_name='Sample Output 3', output_data=b'1 3 1 2 2\n'),
            TestCase(name='sample-4', input_name='Sample Input 4', input_data=b'5\n3 4 10 4 9\n2 7 3 6 9\n', output_name=' Sample Output 4', output_data=b'9 7 3 6 2\n'),
        ])


class AOJArenaProblemTest(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(AOJArenaProblem.from_url('https://onlinejudge.u-aizu.ac.jp/services/room.html#RitsCamp19Day2/problems/A').arena_id, 'RitsCamp19Day2')
        self.assertEqual(AOJArenaProblem.from_url('https://onlinejudge.u-aizu.ac.jp/services/room.html#RitsCamp19Day2/problems/A').alphabet, 'A')
        self.assertEqual(AOJArenaProblem.from_url('https://onlinejudge.u-aizu.ac.jp/services/room.html#ACPC2018Day2/problems/D').alphabet, 'D')
        self.assertEqual(AOJArenaProblem.from_url('https://onlinejudge.u-aizu.ac.jp/services/room.html#ACPC2018Day2/problems/d').alphabet, 'D')
        self.assertIsNone(AOJArenaProblem.from_url('http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=DSL_1_A'))

    def test_download_sample_cases(self):
        self.assertEqual(AOJArenaProblem.from_url('https://onlinejudge.u-aizu.ac.jp/services/room.html#yupro/problems/A').download_sample_cases(), [
            TestCase(name='sample-1', input_name='1', input_data=b'koukyoukoukokukikou\nabrakadabra\nacmicpc\njapaque\nhelloworld\n#\n', output_name='1', output_data=b'0\n2\n4\n5\n7\n'),
        ])

    def test_download_sample_cases_not_registered(self):
        # see: https://github.com/kmyk/online-judge-tools/issues/207
        self.assertEqual(AOJArenaProblem.from_url('https://onlinejudge.u-aizu.ac.jp/services/room.html#RitsCamp18Day3/problems/B').download_sample_cases(), [
            TestCase(name='sample-1', input_name='入力例1', input_data=b'4\n2 0 -2 1\n', output_name='出力例1', output_data=b'1\n1\n'),
            TestCase(name='sample-2', input_name='入力例2', input_data=b'3\n2 -2 -2\n', output_name='出力例2', output_data=b'3\n1\n2\n3\n'),
            TestCase(name='sample-3', input_name='入力例3', input_data=b'2\n-1 0\n', output_name='出力例3', output_data=b'0\n'),
            TestCase(name='sample-4', input_name='入力例4', input_data=b'5\n-1 2 1 -2 -1\n', output_name='出力例4', output_data=b'3\n1\n2\n4\n'),
        ])
