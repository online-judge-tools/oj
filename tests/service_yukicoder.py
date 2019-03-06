# -*- coding: utf-8 -*-
import unittest

from onlinejudge.service.yukicoder import YukicoderProblem, YukicoderService
from onlinejudge.type import *


class YukicoderProblemTest(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(YukicoderProblem.from_url('https://yukicoder.me/problems/no/9003').problem_no, 9003)
        self.assertEqual(YukicoderProblem.from_url('https://yukicoder.me/problems/100').problem_id, 100)
        self.assertEqual(YukicoderProblem.from_url('http://yukicoder.me/problems/no/123/').problem_no, 123)
        self.assertEqual(YukicoderProblem.from_url('http://yukicoder.me/problems/123').problem_id, 123)

    def test_donwload_sample_cases(self):
        self.assertEqual(YukicoderProblem.from_url('http://yukicoder.me/problems/no/9000').download_sample_cases(), [
            TestCase(name='sample-1', input_name='サンプル1 入力', input_data=b'yukicoder\n', output_name='サンプル1 出力', output_data=b'Hello World!\n'),
        ])

        self.assertEqual(YukicoderProblem.from_url('https://yukicoder.me/problems/no/400').download_sample_cases(), [
            TestCase(name='sample-1', input_name='サンプル1 入力', input_data=b'<<<\n', output_name='サンプル1 出力', output_data=b'>>>\n'),
            TestCase(name='sample-2', input_name='サンプル2 入力', input_data=b'<>>\n', output_name='サンプル2 出力', output_data=b'<<>\n'),
            TestCase(name='sample-3', input_name='サンプル3 入力', input_data=b'>>><<<\n', output_name='サンプル3 出力', output_data=b'>>><<<\n'),
            TestCase(name='sample-4', input_name='サンプル4 入力', input_data=b'><<><<<><><\n', output_name='サンプル4 出力', output_data=b'><><>>><>><\n'),
        ])

        self.assertEqual(YukicoderProblem.from_url('https://yukicoder.me/problems/no/260').download_sample_cases(), [
            TestCase(name='sample-1', input_name='サンプル1 入力', input_data=b'1 100\n', output_name='サンプル1 出力', output_data=b'40\n'),
            TestCase(name='sample-2', input_name='サンプル2 入力', input_data=b'114 514\n', output_name='サンプル2 出力', output_data=b'211\n'),
            TestCase(name='sample-3', input_name='サンプル3 入力', input_data=b'1234 567890\n', output_name='サンプル3 出力', output_data=b'339733\n'),
        ])

        self.assertEqual(YukicoderProblem.from_url('https://yukicoder.me/problems/no/104').download_sample_cases(), [
            TestCase(name='sample-1', input_name='サンプル1 入力', input_data=b'LR\n', output_name='サンプル1 出力', output_data=b'5\n'),
            TestCase(name='sample-2', input_name='サンプル2 入力', input_data=b'RLL\n', output_name='サンプル2 出力', output_data=b'12\n'),
            TestCase(name='sample-3', input_name='サンプル3 入力', input_data=b'RLLRLRLRRRLRL\n', output_name='サンプル3 出力', output_data=b'12986\n'),
            TestCase(name='sample-4', input_name='サンプル4 入力', input_data=b'\n', output_name='サンプル4 出力', output_data=b'1\n'),
        ])


class YukicoderOfficialAPITest(unittest.TestCase):
    def test_get_user_10(self):
        data = YukicoderService().get_user(id=10)
        self.assertIn('Id', data)
        self.assertIn('Name', data)
        self.assertIn('Solved', data)
        self.assertIn('Level', data)
        self.assertIn('Rank', data)
        self.assertIn('Score', data)
        self.assertIn('Points', data)
        self.assertEqual(data['Id'], 10)
        self.assertEqual(data['Name'], 'yuki2006')

    def test_get_user_yuki2006(self):
        data = YukicoderService().get_user(name='yuki2006')
        self.assertEqual(data['Id'], 10)
        self.assertEqual(data['Name'], 'yuki2006')

    def test_get_user_0(self):
        data = YukicoderService().get_user(id=0)
        self.assertIs(data, None)

    def test_get_solved_10(self):
        data = YukicoderService().get_solved(id=10)
        self.assertGreater(len(data), 200)
        self.assertIn('No', data[0])
        self.assertIn('ProblemId', data[0])
        self.assertIn('Title', data[0])
        self.assertIn('AuthorId', data[0])
        self.assertIn('TesterId', data[0])
        self.assertIn('Level', data[0])
        self.assertIn('ProblemType', data[0])
        self.assertIn('Tags', data[0])

    def test_get_solved_yuki2006(self):
        data = YukicoderService().get_solved(name='yuki2006')
        self.assertGreater(len(data), 200)

    def test_get_solved_0(self):
        data = YukicoderService().get_solved(id=0)
        self.assertIs(data, None)

    def test_get_user_favorite_10(self):
        data = YukicoderService().get_user_favorite(id=10)
        it = list(filter(lambda row: row['#'] == 10000, data))
        self.assertEqual(len(it), 1)
        it = it[0]
        self.assertEqual(it['問題'], 'No.9000 Hello World! （テスト用）')
        self.assertEqual(it['結果'], 'AC')
        self.assertEqual(it['言語'], 'C++11')

    def test_get_user_favorite_problem_10(self):
        data = YukicoderService().get_user_favorite_problem(id=10)
        it = list(filter(lambda row: row['ナンバー'] == 111, data))
        self.assertEqual(len(it), 1)
        it = it[0]
        self.assertEqual(it['問題名'], 'あばばばば')
        self.assertEqual(it['レベル'], '1.5')

    def test_get_user_favorite_wiki_10(self):
        data = YukicoderService().get_user_favorite_wiki(id=10)
        it = list(filter(lambda row: row['Wikiページ'] == 'decomposable_searching_problem', data))
        self.assertEqual(len(it), 1)

    def test_get_submissions(self):
        data = YukicoderService().get_submissions(page=3, status='TLE')
        self.assertEqual(len(data), 50)
        self.assertEqual(data[4]['結果'], 'TLE')

    def test_get_problems(self):
        data = YukicoderService().get_problems(page=2, sort='no_asc')
        self.assertEqual(len(data), 50)
        self.assertEqual(data[3]['ナンバー'], 54)
        self.assertEqual(data[3]['問題名'], "Happy Hallowe'en")
        self.assertEqual(data[3]['レベル'], '4')
        self.assertEqual(data[3]['作問者/url'], '/users/4')


if __name__ == '__main__':
    unittest.main()
