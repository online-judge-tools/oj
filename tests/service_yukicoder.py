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

    def test_donwload_sample_cases_issue_355(self):
        # see https://github.com/kmyk/online-judge-tools/issues/355
        self.assertEqual(YukicoderProblem.from_url('https://yukicoder.me/problems/no/649').download_sample_cases(), [
            TestCase(name='sample-1', input_name='サンプル1 入力', input_data=b'15 3\n1 3\n1 4\n1 5\n2\n2\n1 10\n1 10\n1 1\n2\n1 3\n2\n1 1000\n2\n1 0\n2\n', output_name='サンプル1 出力', output_data=b'5\n-1\n4\n3\n10\n3\n'),
            TestCase(name='sample-2', input_name='サンプル2 入力', input_data=b'4 1\n1 10\n1 10\n2\n2\n', output_name='サンプル2 出力', output_data=b'10\n10\n'),
            TestCase(name='sample-3', input_name='サンプル3 入力', input_data=b'4 2\n1 9\n1 10000000000000000\n1 90000000000000000\n2\n', output_name='サンプル3 出力', output_data=b'10000000000000000\n'),
            TestCase(name='sample-4', input_name='サンプル4 入力', input_data=b'1 1\n2\n', output_name='サンプル4 出力', output_data=b'-1\n'),
        ])

    def test_donwload_sample_cases_issue_192(self):
        # see https://github.com/kmyk/online-judge-tools/issues/192
        self.assertEqual(YukicoderProblem.from_url('https://yukicoder.me/problems/no/750').download_sample_cases(), [
            TestCase(name='sample-1', input_name='サンプル1 入力', input_data=b'6\n4 5\n3 7\n3 4\n-2 3\n9 1\n3 8\n', output_name='サンプル1 出力', output_data=b'9 1\n4 5\n3 4\n3 7\n3 8\n-2 3\n'),
            TestCase(name='sample-2', input_name='サンプル2 入力', input_data=b'3\n3 7\n1 1\n5 3\n', output_name='サンプル2 出力', output_data=b'5 3\n1 1\n3 7\n'),
            TestCase(name='sample-3', input_name='サンプル3 入力', input_data=b'6\n1 1\n7 4\n0 5\n1 3\n-8 9\n5 1\n', output_name='サンプル3 出力', output_data=b'5 1\n7 4\n1 1\n1 3\n0 5\n-8 9\n'),
        ])
        self.assertEqual(YukicoderProblem.from_url('https://yukicoder.me/problems/no/751').download_sample_cases(), [
            TestCase(name='sample-1', input_name='サンプル1 入力', input_data=b'3\n1 8 3\n2\n6 10\n', output_name='サンプル1 出力', output_data=b'5 72\n'),
            TestCase(name='sample-2', input_name='サンプル2 入力', input_data=b'2\n-1 1\n3\n-1 1 -1\n', output_name='サンプル2 出力', output_data=b'-1 1\n'),
        ])

    def test_get_handmade_cases_issue_553(self):
        # see https://github.com/kmyk/online-judge-tools/issues/553
        handmade_html = """
<!DOCTYPE html>
<html lang="ja">
<head>
</head>
<body>
<div class="block">
    <div class="sample">
        <h5 class="underline">サンプル1</h5>
        <div class="paragraph">
            <h6>入力</h6>
            <pre><strong>3<br/>1</strong> 2<br/>3 4<br/>5 6</pre>
            <h6>出力</h6>
            <pre>0<br/><br/><br/><br/><br/>0</pre>
        </div>
    </div>

    <div class="sample">
        <h5 class="underline">サンプル2</h5>
        <div class="paragraph">
            <h6>入力</h6>
            <pre>1 1 1
1 <strong><mark>0</mark></strong> 1
1 1 1</pre>
            <h6>出力</h6>
            <pre><s>0</s></pre>
        </div>
    </div>

    <div class="sample">
        <h5 class="underline">サンプル3</h5>
        <div class="paragraph">
            <h6>入力</h6>
            <pre><i></i></pre>
            <h6>出力</h6>
            <pre><i><strong>We<br/><mark>Love</mark><br/><s>Competitive</s><br/>Programming!</strong></i></pre>
        </div>
    </div>
</div>
</body>
</html>
"""
        self.assertEqual(YukicoderProblem.from_nothing().get_handmade_sample_cases(html=handmade_html), [
            TestCase(name='sample-1', input_name='サンプル1 入力', input_data=b'3\n1 2\n3 4\n5 6\n', output_name='サンプル1 出力', output_data=b'0\n\n\n\n\n0\n'),
            TestCase(name='sample-2', input_name='サンプル2 入力', input_data=b'1 1 1\n1 0 1\n1 1 1\n', output_name='サンプル2 出力', output_data=b'0\n'),
            TestCase(name='sample-3', input_name='サンプル3 入力', input_data=b'\n', output_name='サンプル3 出力', output_data=b'We\nLove\nCompetitive\nProgramming!\n'),
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
        self.assertIsNone(data)

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
        self.assertIsNone(data)

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
        self.assertEqual(it['レベル'], '1')

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


class YukicoderProblemGetInputFormatTest(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(YukicoderProblem.from_url('https://yukicoder.me/problems/no/1').get_input_format(), '\\(N\\)\n\\(C\\)\n\\(V\\)\n\\(S_1\\ S_2\\ S_3\\ \\dots\\ S_V\\)\n\\(T_1\\ T_2\\ T_3\\ \\dots\\ T_V\\)\n\\(Y_1\\ Y_2\\ Y_3\\ \\dots\\ Y_V\\)\n\\(M_1\\ M_2\\ M_3\\ \\dots\\ M_V\\)\n')
        self.assertEqual(YukicoderProblem.from_url('https://yukicoder.me/problems/no/2').get_input_format(), 'N\n')
        self.assertEqual(YukicoderProblem.from_url('https://yukicoder.me/problems/no/3').get_input_format(), 'N\n')
        self.assertEqual(YukicoderProblem.from_url('https://yukicoder.me/problems/no/128').get_input_format(), 'N\nM')
        self.assertEqual(YukicoderProblem.from_url('https://yukicoder.me/problems/no/256').get_input_format(), '$N$\n')
        self.assertEqual(YukicoderProblem.from_url('https://yukicoder.me/problems/no/512').get_input_format(), '$X$ $Y$\n$N$\n$A_1$ $\\cdots$ $A_N$\n')
        self.assertEqual(YukicoderProblem.from_url('https://yukicoder.me/problems/no/777').get_input_format(), '$N$\n$A_1$ $B_1$ $C_1$\n$A_2$ $B_2$ $C_2$\n…\n$A_N$ $B_N$ $C_N$\n')

    def test_problem_without_input(self):
        self.assertIsNone(YukicoderProblem.from_url('https://yukicoder.me/problems/no/3003').get_input_format())


if __name__ == '__main__':
    unittest.main()
