# -*- coding: utf-8 -*-
import unittest

import requests

from onlinejudge.service.atcoder import AtCoderContest, AtCoderProblem, AtCoderProblemDetailedData, AtCoderService, AtCoderSubmission
from onlinejudge.type import TestCase


class AtCoderSerivceTest(unittest.TestCase):
    def test_from_url(self):
        self.assertIsInstance(AtCoderService.from_url('https://atcoder.jp/'), AtCoderService)
        self.assertIsInstance(AtCoderService.from_url('https://beta.atcoder.jp/'), AtCoderService)
        self.assertIsInstance(AtCoderService.from_url('https://abc001.contest.atcoder.jp/'), AtCoderService)
        self.assertIsInstance(AtCoderService.from_url('https://atcoder.jp/contests/agc001/submissions/806160'), AtCoderService)
        self.assertIsNone(AtCoderService.from_url('https://codeforces.com/'))

    def test_iterate_contests(self):
        contests = list(AtCoderService().iterate_contests())
        contest_ids = [contest.contest_id for contest in contests]
        self.assertIn('arc001', contest_ids)
        self.assertIn('abc100', contest_ids)
        self.assertIn('kupc2012', contest_ids)
        contest, = [contest for contest in contests if contest.contest_id == 'utpc2013']
        data = contest.download_data()
        self.assertEqual(data.start_time.year, 2014)
        self.assertEqual(data.start_time.month, 3)
        self.assertEqual(data.start_time.day, 2)
        self.assertEqual(data.name, '東京大学プログラミングコンテスト2013')
        self.assertEqual(data.duration.total_seconds(), 5 * 60 * 60)
        self.assertEqual(data.rated_range, '-')


class AtCoderContestTest(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(AtCoderContest.from_url('https://kupc2014.contest.atcoder.jp/tasks/kupc2014_d').contest_id, 'kupc2014')
        self.assertEqual(AtCoderContest.from_url('https://atcoder.jp/contests/agc030').contest_id, 'agc030')
        self.assertIsNone(AtCoderContest.from_url('https://atcoder.jp/contests/'))

    def test_load_details(self):
        contest = AtCoderContest.from_url('https://atcoder.jp/contests/keyence2019')
        self.assertEqual(contest.download_data(lang='en').name, 'KEYENCE Programming Contest 2019')
        self.assertEqual(contest.download_data(lang='ja').name, 'キーエンス プログラミング コンテスト 2019')
        data = contest.download_data()
        self.assertEqual(data.start_time.year, 2019)
        self.assertEqual(data.start_time.month, 1)
        self.assertEqual(data.start_time.day, 13)
        self.assertEqual(data.duration.total_seconds(), 2 * 60 * 60)
        self.assertEqual(data.can_participate, 'All')
        self.assertEqual(data.rated_range, ' ~ 2799')
        self.assertEqual(data.penalty.total_seconds(), 5 * 60)

        contest = AtCoderContest.from_url('https://atcoder.jp/contests/dp')
        self.assertEqual(contest.download_data(lang='ja').name, 'Educational DP Contest / DP まとめコンテスト')
        self.assertEqual(contest.download_data(lang='en').name, 'Educational DP Contest')
        data = contest.download_data()
        self.assertEqual(data.start_time.year, 2019)
        self.assertEqual(data.start_time.month, 1)
        self.assertEqual(data.start_time.day, 6)
        self.assertEqual(data.duration.total_seconds(), 5 * 60 * 60)
        self.assertEqual(data.can_participate, 'All')
        self.assertEqual(data.rated_range, '-')
        self.assertEqual(data.penalty.total_seconds(), 5 * 60)

    def test_get_penalty_a_singular_form(self):
        contest = AtCoderContest.from_url('https://atcoder.jp/contests/chokudai_S002')
        self.assertEqual(contest.download_data().penalty.total_seconds(), 60)  # Penalty is written as "1 minute", not  "1 minutes"

    def test_list_problems(self):
        contest = AtCoderContest.from_url('https://atcoder.jp/contests/agc028')
        problems = contest.list_problems()
        self.assertEqual(len(problems), 7)
        self.assertEqual(problems[0].download_data().alphabet, 'A')
        self.assertEqual(problems[0].download_data().name, 'Two Abbreviations')
        self.assertEqual(problems[0].download_data().time_limit_msec, 2000)
        self.assertEqual(problems[0].download_data().memory_limit_byte, 1024 * 1000 * 1000)
        self.assertEqual(problems[5].download_data().alphabet, 'F')
        self.assertEqual(problems[5].problem_id, 'agc028_f')
        self.assertEqual(problems[6].download_data().alphabet, 'F2')
        self.assertEqual(problems[6].problem_id, 'agc028_f2')

    def test_list_problems_with_float_values(self):
        """
        .. seealso:
            https://github.com/kmyk/online-judge-tools/issues/412
        """

        contest = AtCoderContest.from_url('https://atcoder.jp/contests/dwacon2018-final-open')
        problems = contest.list_problems()
        self.assertEqual(problems[0].download_data().time_limit_msec, 2525)
        self.assertEqual(problems[0].download_data().memory_limit_byte, int(252.525 * 1000 * 1000))
        self.assertEqual(problems[1].download_data().time_limit_msec, 5252)
        self.assertEqual(problems[1].download_data().memory_limit_byte, int(525.252 * 1000 * 1000))

    def test_list_problems_time_limit_is_less_than_msec(self):
        contest = AtCoderContest.from_url('https://atcoder.jp/contests/joi2019ho')
        problems = contest.list_problems()
        self.assertEqual(problems[0].download_data().time_limit_msec, 1000)
        self.assertEqual(problems[1].download_data().time_limit_msec, 1000)
        self.assertEqual(problems[2].download_data().time_limit_msec, 500)
        self.assertEqual(problems[3].download_data().time_limit_msec, 1000)
        self.assertEqual(problems[4].download_data().time_limit_msec, 2000)

    def test_list_problems_memory_limit_is_zero(self):
        contest = AtCoderContest.from_url('https://atcoder.jp/contests/future-contest-2019-final-open')
        problems = contest.list_problems()
        self.assertEqual(problems[0].download_data().memory_limit_byte, 1024 * 1000 * 1000)  # 1024 MB
        self.assertEqual(problems[1].download_data().memory_limit_byte, 0)  # 0 KB

    def test_iterate_submissions(self):
        contest = AtCoderContest.from_url('https://atcoder.jp/contests/code-festival-2014-exhibition-open')
        submissions = list(contest.iterate_submissions())
        self.assertGreater(len(submissions), 300)
        self.assertEqual(submissions[0].download_data().code_size, 276)
        self.assertEqual(submissions[0].download_data().status, 'WA')
        self.assertEqual(submissions[1].download_data().user_id, 'snuke')
        self.assertEqual(submissions[1].download_data().status, 'WA')

    def test_get_contest_without_penalty(self):
        contest = AtCoderContest.from_url('https://atcoder.jp/contests/otemae2019')
        self.assertEqual(contest.download_data(lang='ja').name, '大手前プロコン 2019')
        self.assertEqual(contest.download_data().penalty.total_seconds(), 0)  # This contest has no penalty
        self.assertEqual(contest.download_data(lang='en').name, 'Otemae High School Programming Contest 2019')
        self.assertEqual(contest.download_data().penalty.total_seconds(), 0)  # This contest has no penalty


class AtCoderProblemTest(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(AtCoderProblem.from_url('https://kupc2014.contest.atcoder.jp/tasks/kupc2014_d').contest_id, 'kupc2014')
        self.assertEqual(AtCoderProblem.from_url('https://kupc2014.contest.atcoder.jp/tasks/kupc2014_d').problem_id, 'kupc2014_d')
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/agc030/tasks/agc030_c').contest_id, 'agc030')
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/agc030/tasks/agc030_c').problem_id, 'agc030_c')

    def test_repr(self):
        self.assertEqual(repr(AtCoderProblem(contest_id='kupc2014', problem_id='kupc2014_d')), "AtCoderProblem.from_url('https://atcoder.jp/contests/kupc2014/tasks/kupc2014_d')")
        self.assertEqual(repr(AtCoderProblem(contest_id='agc030', problem_id='agc030_c')), "AtCoderProblem.from_url('https://atcoder.jp/contests/agc030/tasks/agc030_c')")
        self.assertEqual(repr(AtCoderProblem(contest_id='xxxxxx', problem_id='yyyyyy')), "AtCoderProblem.from_url('https://atcoder.jp/contests/xxxxxx/tasks/yyyyyy')")

    def test_eq(self):
        self.assertEqual(AtCoderProblem.from_url('https://kupc2014.contest.atcoder.jp/tasks/kupc2014_d'), AtCoderProblem.from_url('https://atcoder.jp/contests/kupc2014/tasks/kupc2014_d'))
        self.assertNotEqual(AtCoderProblem.from_url('https://kupc2014.contest.atcoder.jp/tasks/kupc2014_d'), AtCoderProblem.from_url('https://atcoder.jp/contests/agc030/tasks/agc030_c'))

    def test_load_details(self):
        problem = AtCoderProblem.from_url('https://atcoder.jp/contests/abc118/tasks/abc118_a')
        data = problem.download_data()
        self.assertEqual(data.alphabet, 'A')
        self.assertEqual(data.name, 'B +/- A')
        self.assertEqual(data.time_limit_msec, 2000)
        self.assertEqual(data.memory_limit_byte, 1024 * 1000 * 1000)
        self.assertEqual(data.score, 100)

    def test_get_alphabet(self):
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/agc028/tasks/agc028_f').download_data().alphabet, 'F')
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/agc028/tasks/agc028_f2').download_data().alphabet, 'F2')

    def test_get_score(self):
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/future-contest-2018-final/tasks/future_contest_2018_final_a').download_data().score, 50000000)
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/abc001/tasks/abc001_4').download_data().score, None)

    def test_get_score_latex(self):
        """
        .. seealso::
            https://github.com/kmyk/online-judge-tools/issues/411
        """

        self.assertIsNone(AtCoderProblem.from_url('https://atcoder.jp/contests/wupc2019/tasks/wupc2019_a').download_data().score)

    def test_get_time_limit_is_less_than_msec(self):
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/joi2019ho/tasks/joi2019ho_c').download_data().time_limit_msec, 500)
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/future-contest-2019-qual/tasks/future_contest_2019_qual_b').download_data().time_limit_msec, 0)

    def test_get_memory_limit_is_zero(self):
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/future-contest-2019-qual/tasks/future_contest_2019_qual_b').download_data().memory_limit_byte, 0)

    def test_iterate_submissions(self):
        problem = AtCoderProblem.from_url('https://atcoder.jp/contests/abc119/tasks/abc119_c')
        submissions = problem.iterate_submissions()
        self.assertEqual(next(submissions).download_data().score, 300)
        self.assertEqual(next(submissions).download_data().code_size, 1208)
        self.assertEqual(next(submissions).download_data().exec_time_msec, 2)
        self.assertEqual(next(submissions).download_data().memory_byte, 256 * 1000)


class AtCoderSubmissionTest(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(AtCoderSubmission.from_url('https://atcoder.jp/contests/kupc2012/submissions/2097011').contest_id, 'kupc2012')
        self.assertEqual(AtCoderSubmission.from_url('https://atcoder.jp/contests/kupc2012/submissions/2097011').submission_id, 2097011)
        self.assertEqual(AtCoderSubmission.from_url('https://qupc2014.contest.atcoder.jp/submissions/1444440').contest_id, 'qupc2014')
        self.assertEqual(AtCoderSubmission.from_url('https://qupc2014.contest.atcoder.jp/submissions/1444440').submission_id, 1444440)

    def test_submission_info(self):
        submission = AtCoderSubmission.from_url('https://atcoder.jp/contests/agc030/submissions/3904911')
        data = submission.download_data()
        self.assertEqual(data.submission_time.year, 2018)
        self.assertEqual(data.submission_time.month, 12)
        self.assertEqual(data.submission_time.day, 31)
        self.assertEqual(data.user_id, 'kimiyuki')
        self.assertEqual(data.problem.problem_id, 'agc030_b')
        self.assertEqual(data.language_name, 'C++14 (GCC 5.4.1)')
        self.assertEqual(data.score, 800)
        self.assertEqual(data.code_size, 1457)
        self.assertEqual(data.status, 'AC')
        self.assertEqual(data.exec_time_msec, 85)
        self.assertEqual(data.memory_byte, 3328 * 1000)

    def test_submission_info_compile_error(self):
        submission = AtCoderSubmission.from_url('https://atcoder.jp/contests/abc124/submissions/4943518')
        data = submission.download_data()
        self.assertEqual(data.submission_time.year, 2019)
        self.assertEqual(data.submission_time.month, 4)
        self.assertEqual(data.submission_time.day, 13)
        self.assertEqual(data.user_id, 'pekempey')
        self.assertEqual(data.problem.problem_id, 'abc124_d')
        self.assertEqual(data.language_name, 'Rust (1.15.1)')
        self.assertEqual(data.score, 0)
        self.assertEqual(data.code_size, 787)
        self.assertEqual(data.status, 'CE')
        self.assertEqual(data.exec_time_msec, None)
        self.assertEqual(data.memory_byte, None)

    def test_submission_info_compile_warnings(self):
        submission = AtCoderSubmission.from_url('https://atcoder.jp/contests/agc032/submissions/4675493')
        data = submission.download_data()
        self.assertEqual(data.submission_time.year, 2019)
        self.assertEqual(data.submission_time.month, 3)
        self.assertEqual(data.submission_time.day, 23)
        self.assertEqual(data.user_id, 'yutaka1999')
        self.assertEqual(data.problem.problem_id, 'agc032_e')
        self.assertEqual(data.language_name, 'C++14 (GCC 5.4.1)')
        self.assertEqual(data.score, 0)
        self.assertEqual(data.code_size, 1682)
        self.assertEqual(data.status, 'WA')
        self.assertEqual(data.exec_time_msec, 392)
        self.assertEqual(data.memory_byte, 7168 * 1000)

    def test_get_test_sets(self):
        submission = AtCoderSubmission.from_url('https://atcoder.jp/contests/arc028/submissions/223928')
        test_cases = submission.download_data().test_sets
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
        test_cases = submission.download_data().test_cases
        self.assertEqual(len(test_cases), 2)
        self.assertEqual(test_cases[0].case_name, 'input_01.txt')
        self.assertEqual(test_cases[0].status, 'TLE')
        self.assertEqual(test_cases[0].exec_time_msec, 2031)
        self.assertEqual(test_cases[0].memory_byte, 9220000)
        self.assertEqual(test_cases[1].case_name, 'input_02.txt')
        self.assertEqual(test_cases[1].status, 'AC')
        self.assertEqual(test_cases[1].exec_time_msec, 131)
        self.assertEqual(test_cases[1].memory_byte, 7400 * 1000)

    def test_get_source_code(self):
        submission = AtCoderSubmission.from_url('https://atcoder.jp/contests/abc100/submissions/3082514')
        self.assertEqual(submission.download_data().source_code, b'/9\\|\\B/c:(\ncYay!')
        self.assertEqual(submission.download_data().code_size, 16)

        submission = AtCoderSubmission.from_url('https://atcoder.jp/contests/abc100/submissions/4069980')
        self.assertEqual(submission.download_data().source_code, b'/9\\|\\B/c:(\r\ncYay!')
        self.assertEqual(submission.download_data().code_size, 17)

        submission = AtCoderSubmission.from_url('https://atcoder.jp/contests/abc100/submissions/4317534')
        self.assertEqual(submission.download_data().source_code, b'/9\\|\\B/c:(\r\ncYay!\r\n')
        self.assertEqual(submission.download_data().code_size, 19)

    def test_get_score_float(self):
        submission = AtCoderSubmission.from_url('https://atcoder.jp/contests/pakencamp-2018-day3/submissions/4583531')
        self.assertAlmostEqual(submission.download_data().score, 32.53)


class AtCoderProblemDataTest(unittest.TestCase):
    # test the third format (stated in AtCoderProblemDetailedData)
    def test_from_html_1(self):
        url = 'https://atcoder.jp/contests/abc114/tasks/abc114_d'
        resp = requests.get(url)
        html = resp.content.decode(resp.apparent_encoding)
        data = AtCoderProblemDetailedData.from_html(html, problem=AtCoderProblem.from_url(url))

        self.assertEqual(data.alphabet, 'D')
        self.assertEqual(data.available_languages, None)
        self.assertEqual(data.html, html)
        self.assertEqual(data.input_format, '<var>N</var>\r\n')
        self.assertEqual(data.memory_limit_byte, 1024 * 1000 * 1000)
        self.assertEqual(data.name, '756')
        self.assertEqual(data.problem, AtCoderProblem.from_url(url))
        self.assertEqual(data.sample_cases, [
            TestCase(name='sample-1', input_name='入力例 1', input_data=b'9\n', output_name='出力例 1', output_data=b'0\n'),
            TestCase(name='sample-2', input_name='入力例 2', input_data=b'10\n', output_name='出力例 2', output_data=b'1\n'),
            TestCase(name='sample-3', input_name='入力例 3', input_data=b'100\n', output_name='出力例 3', output_data=b'543\n'),
        ])
        self.assertEqual(data.score, 400)
        self.assertEqual(data.time_limit_msec, 2 * 1000)

    # test the second format (stated in AtCoderProblemDetailedData)
    def test_from_html_2(self):
        url = 'https://atcoder.jp/contests/abc003/tasks/abc003_4'
        resp = requests.get(url)
        html = resp.content.decode(resp.apparent_encoding)
        data = AtCoderProblemDetailedData.from_html(html, problem=AtCoderProblem.from_url(url))

        self.assertEqual(data.alphabet, 'D')
        self.assertEqual(data.available_languages, None)
        self.assertEqual(data.html, html)
        self.assertEqual(data.input_format, '\r\n<var>R</var> <var>C</var>\r\n<var>X</var> <var>Y</var>\r\n<var>D</var> <var>L</var>\r\n')
        self.assertEqual(data.memory_limit_byte, 64 * 1000 * 1000)
        self.assertEqual(data.name, 'AtCoder社の冬')
        self.assertEqual(data.problem, AtCoderProblem.from_url(url))
        self.assertEqual(data.sample_cases, [
            TestCase(name='sample-1', input_name='入力例 1', input_data=b'3 2\n2 2\n2 2\n', output_name='出力例 1', output_data=b'12\n'),
            TestCase(name='sample-2', input_name='入力例 2', input_data=b'4 5\n3 1\n3 0\n', output_name='出力例 2', output_data=b'10\n'),
            TestCase(name='sample-3', input_name='入力例 3', input_data=b'23 18\n15 13\n100 95\n', output_name='出力例 3', output_data=b'364527243\n'),
            TestCase(name='sample-4', input_name='入力例 4', input_data=b'30 30\n24 22\n145 132\n', output_name='出力例 4', output_data=b'976668549\n'),
        ])
        self.assertEqual(data.score, None)
        self.assertEqual(data.time_limit_msec, 2 * 1000)

    # test the second format (stated in AtCoderProblemDetailedData)
    # (see https://github.com/kmyk/online-judge-tools/issues/106)
    def test_from_html_3(self):
        url = 'https://atcoder.jp/contests/utpc2011/tasks/utpc2011_1'
        resp = requests.get(url)
        html = resp.content.decode(resp.apparent_encoding)
        data = AtCoderProblemDetailedData.from_html(html, problem=AtCoderProblem.from_url(url))

        self.assertEqual(data.alphabet, 'A')
        self.assertEqual(data.available_languages, None)
        self.assertEqual(data.html, html)
        #self.assertEqual(data.input_format, '')
        self.assertEqual(data.memory_limit_byte, 300 * 1000 * 1000)
        self.assertEqual(data.name, 'プログラミングコンテスト')
        self.assertEqual(data.problem, AtCoderProblem.from_url(url))
        self.assertEqual(data.sample_cases, [
            TestCase(name='sample-1', input_name='入力例 1:', input_data=b'3 4\n1 0 1 0\n1 1 1 0\n0 0 0 1\n', output_name='入力例 1 に対する出力例:', output_data=b'3\n'),
            TestCase(name='sample-2', input_name='入力例 2:', input_data=b'3 4\n1 1 1 1\n1 1 1 1\n1 1 1 1\n', output_name='入力例 2 に対する出力例:', output_data=b'4\n'),
            TestCase(name='sample-3', input_name='入力例 3:', input_data=b'1 1\n0\n', output_name='入力例 3 に対する出力例:', output_data=b'0\n'),
        ])
        self.assertEqual(data.score, None)
        self.assertEqual(data.time_limit_msec, 1 * 1000)

    # deal with empty output case (see https://github.com/kmyk/online-judge-tools/issues/507)
    def test_from_html_4(self):
        url = 'https://atcoder.jp/contests/agc036/tasks/agc036_b'
        resp = requests.get(url)
        html = resp.content.decode(resp.apparent_encoding)
        data = AtCoderProblemDetailedData.from_html(html, problem=AtCoderProblem.from_url(url))

        self.assertEqual(data.alphabet, 'B')
        self.assertEqual(data.available_languages, None)
        self.assertEqual(data.html, html)
        self.assertEqual(data.input_format, '<var>N</var> <var>K</var>\r\n<var>A_0</var> <var>A_1</var> <var>\cdots</var> <var>A_{N-1}</var>\r\n')
        self.assertEqual(data.memory_limit_byte, 1024 * 1000 * 1000)
        self.assertEqual(data.name, 'Do Not Duplicate')
        self.assertEqual(data.problem, AtCoderProblem.from_url(url))
        self.assertEqual(data.sample_cases, [
            TestCase(name='sample-1', input_name='入力例 1', input_data=b'3 2\n1 2 3\n', output_name='出力例 1', output_data=b'2 3\n'),
            TestCase(name='sample-2', input_name='入力例 2', input_data=b'5 10\n1 2 3 2 3\n', output_name='出力例 2', output_data=b'3\n'),
            TestCase(name='sample-3', input_name='入力例 3', input_data=b'6 1000000000000\n1 1 2 2 3 3\n', output_name='出力例 3', output_data=b'\n'),
            TestCase(name='sample-4', input_name='入力例 4', input_data=b'11 97\n3 1 4 1 5 9 2 6 5 3 5\n', output_name='出力例 4', output_data=b'9 2 6\n'),
        ])
        self.assertEqual(data.score, 700)
        self.assertEqual(data.time_limit_msec, 2 * 1000)

    def test_from_html_5(self):
        url = 'https://atcoder.jp/contests/tenka1-2013-quala/tasks/tenka1_2013_qualA_a'
        resp = requests.get(url)
        html = resp.content.decode(resp.apparent_encoding)
        data = AtCoderProblemDetailedData.from_html(html, problem=AtCoderProblem.from_url(url))

        self.assertEqual(data.alphabet, 'A')
        self.assertEqual(data.available_languages, None)
        self.assertEqual(data.html, html)
        self.assertEqual(data.input_format, None)
        self.assertEqual(data.memory_limit_byte, 64 * 1000 * 1000)
        self.assertEqual(data.name, '天下一株式会社採用情報')
        self.assertEqual(data.problem, AtCoderProblem.from_url(url))
        self.assertEqual(data.sample_cases, [])
        self.assertEqual(data.score, None)
        self.assertEqual(data.time_limit_msec, 2 * 1000)

    # (see https://github.com/kmyk/online-judge-tools/issues/414)
    def test_from_html_6(self):
        url = 'https://atcoder.jp/contests/fuka5/tasks/fuka_graphcut'
        resp = requests.get(url)
        html = resp.content.decode(resp.apparent_encoding)
        data = AtCoderProblemDetailedData.from_html(html, problem=AtCoderProblem.from_url(url))

        self.assertEqual(data.alphabet, 'G')
        self.assertEqual(data.available_languages, None)
        self.assertEqual(data.html, html)
        #self.assertEqual(data.input_format, '')
        self.assertEqual(data.memory_limit_byte, 256 * 1000 * 1000)
        self.assertEqual(data.name, 'Graph Cut')
        self.assertEqual(data.problem, AtCoderProblem.from_url(url))
        self.assertEqual(data.sample_cases, [
            TestCase(name='sample-1', input_name='Sample Input', input_data=b'10 10 0.4000 0.20\n\
.##...###.\n\
.##.####..\n\
.######...\n\
.#.#.####.\n\
######....\n\
##.##.....\n\
....#.....\n\
..####.#..\n\
.#####.##.\n\
.#####.##.\n\
25 38 0.5 0.24\n\
...........#...............#..........\n\
...........###..........####..........\n\
....##.....#####.......####...........\n\
.....##.....###############.....##....\n\
............#####.###.#####......#....\n\
............#########.####............\n\
.....##......#########.###............\n\
....##......#####.#########........#..\n\
....#......##.##..####..####..........\n\
.......#...###########.#####...#......\n\
.......##.##################..##......\n\
........#####.####.##.######.##.......\n\
..........####################........\n\
.........##.##..########..#####.......\n\
.......######....##..#....###.##......\n\
......###.####...##.##..#####.##.#....\n\
....###..##..#...#####..#..########...\n\
..####..###.....#######......#######..\n\
...#######......#######........###....\n\
..####.........##.######........###...\n\
...............###...###..............\n\
..............#######..#...#...##.....\n\
.........#....##########...#....#.....\n\
..#.....##.....########...............\n\
...............########...............\n\
0 0 0 0\n', output_name='Sample Output', output_data=b'11.200000\n\
.##...###.\n\
.##.####..\n\
.######...\n\
.######...\n\
######....\n\
##.##.....\n\
....#.....\n\
..####....\n\
.#####.##.\n\
.#####.##.\n\
73.540000\n\
...........#...............#..........\n\
...........###..........####..........\n\
...........#####.......####...........\n\
............###############...........\n\
............###############...........\n\
............##############............\n\
.............#############............\n\
............###############...........\n\
...........#################..........\n\
.......#...#################...#......\n\
.......##.##################..##......\n\
........####################.##.......\n\
..........####################........\n\
.........#####..########..#####.......\n\
.......######....#####....######......\n\
......########...#####..########.#....\n\
....#######..#...#####..#..########...\n\
..#########.....#######......#######..\n\
...#######......#######........###....\n\
..####.........#########........###...\n\
...............#########..............\n\
..............##########..............\n\
..............##########..............\n\
...............########...............\n\
...............########...............\n'),
        ])
        self.assertEqual(data.score, None)
        self.assertEqual(data.time_limit_msec, 5 * 1000)


class AtCoderProblemGetInputFormatTest(unittest.TestCase):
    def test_normal(self):
        """
        .. code-block:: html

            <div class="io-style">
                <div class="part">
                    <section>
                        <h3>入力</h3>
                        <p>入力は以下の形式で標準入力から与えられる。</p>
                        <pre>
                            <var>N</var>
                        </pre>
                    </section>
                </div>
                <div class="part">
                    ...
                </div>
                ...
            </div>
        """

        self.assertEqual(AtCoderProblem.from_url('https://beta.atcoder.jp/contests/agc001/tasks/agc001_d').download_data().input_format, '<var>N</var> <var>M</var>\r\n<var>A_1</var> <var>A_2</var> <var>...</var> <var>A_M</var>\r\n')
        self.assertEqual(AtCoderProblem.from_url('https://beta.atcoder.jp/contests/agc002/tasks/agc002_d').download_data().input_format, '\r\n<var>N</var> <var>M</var>\r\n<var>a_1</var> <var>b_1</var>\r\n<var>a_2</var> <var>b_2</var>\r\n<var>:</var>\r\n<var>a_M</var> <var>b_M</var>\r\n<var>Q</var>\r\n<var>x_1</var> <var>y_1</var> <var>z_1</var>\r\n<var>x_2</var> <var>y_2</var> <var>z_2</var>\r\n<var>:</var>\r\n<var>x_Q</var> <var>y_Q</var> <var>z_Q</var>\r\n')
        self.assertEqual(AtCoderProblem.from_url('https://beta.atcoder.jp/contests/agc003/tasks/agc003_d').download_data().input_format, '<var>N</var>\r\n<var>s_1</var>\r\n:\r\n<var>s_N</var>\r\n')
        self.assertEqual(AtCoderProblem.from_url('https://beta.atcoder.jp/contests/agc004/tasks/agc004_d').download_data().input_format, '<var>N</var> <var>K</var>\r\n<var>a_1</var> <var>a_2</var> <var>...</var> <var>a_N</var>\r\n')
        self.assertEqual(AtCoderProblem.from_url('https://beta.atcoder.jp/contests/agc005/tasks/agc005_d').download_data().input_format, '<var>N</var> <var>K</var>\r\n')

        self.assertEqual(AtCoderProblem.from_url('https://beta.atcoder.jp/contests/arc083/tasks/arc083_a').download_data().input_format, '<var>A</var> <var>B</var> <var>C</var> <var>D</var> <var>E</var> <var>F</var>\r\n')

    def test_old_problem(self):
        """
        :note: https://github.com/kmyk/online-judge-tools/issues/380

        .. code-block:: html

            <h3>入力</h3>
            <section>
                入力は以下の形式で与えられる。
                <pre>
                    <var>N</var>
                </pre>
            </section>
        """

        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/arc001/tasks/arc001_1').download_data().input_format, '\r\n<var>N</var>\r\n<var>c_1c_2c_3…c_N</var>\r\n')
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/arc002/tasks/arc002_3').download_data().input_format, '\r\n<var>N</var>\r\n<var>c_{1}c_{2}...c_{N}</var>\r\n')
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/arc034/tasks/arc034_4').download_data().input_format, '\r\n<var>A</var> <var>B</var> <var>C</var>\r\n<var>a_1</var> <var>a_2</var> .. <var>a_A</var>\r\n<var>b_1</var> <var>b_2</var> .. <var>b_B</var>\r\n')

    def test_dwacon_problem(self):
        """
        :note: https://github.com/kmyk/online-judge-tools/issues/142

        .. code-block:: html

            <h3 id="入力">入力</h3>
            <p>入力は以下の形式で標準入力から与えられる。</p>
            <div class="io-style">
                <pre>
                    <var>N</var>
                </pre>
            </div>
        """

        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/dwacon2018-final/tasks/dwacon2018_final_a').download_data().input_format, '\r\n<var>H</var> <var>M</var> <var>S</var>\r\n<var>C_1</var> <var>C_2</var>\r\n')
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/dwacon2018-final/tasks/dwacon2018_final_b').download_data().input_format, '\r\n<var>N</var> <var>K</var>\r\n<var>v_1</var> <var>...</var> <var>v_N</var>\r\n')

    def test_problem_without_input(self):
        self.assertIsNone(AtCoderProblem.from_url('https://atcoder.jp/contests/tenka1-2013-quala/tasks/tenka1_2013_qualA_a').download_data().input_format)

    def test_problem_without_input_format(self):
        self.assertIsNone(AtCoderProblem.from_url('https://atcoder.jp/contests/joi2006ho/tasks/joi2006ho_a').download_data().input_format)


if __name__ == '__main__':
    unittest.main()
