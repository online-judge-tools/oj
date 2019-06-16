# -*- coding: utf-8 -*-
import unittest

import requests

from onlinejudge.service.atcoder import AtCoderContest, AtCoderProblem, AtCoderProblemContent, AtCoderService, AtCoderSubmission
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
        self.assertEqual(contest.get_start_time().year, 2014)
        self.assertEqual(contest.get_start_time().month, 3)
        self.assertEqual(contest.get_start_time().day, 2)
        self.assertEqual(contest.get_name(), '東京大学プログラミングコンテスト2013')
        self.assertEqual(contest.get_duration().total_seconds(), 5 * 60 * 60)
        self.assertEqual(contest.get_rated_range(), 'All')


class AtCoderContestTest(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(AtCoderContest.from_url('https://kupc2014.contest.atcoder.jp/tasks/kupc2014_d').contest_id, 'kupc2014')
        self.assertEqual(AtCoderContest.from_url('https://atcoder.jp/contests/agc030').contest_id, 'agc030')
        self.assertIsNone(AtCoderContest.from_url('https://atcoder.jp/contests/'))

    def test_load_details(self):
        contest = AtCoderContest.from_url('https://atcoder.jp/contests/keyence2019')
        self.assertEqual(contest.get_name(lang='en'), 'KEYENCE Programming Contest 2019')
        self.assertEqual(contest.get_name(lang='ja'), 'キーエンス プログラミング コンテスト 2019')
        self.assertEqual(contest.get_start_time().year, 2019)
        self.assertEqual(contest.get_start_time().month, 1)
        self.assertEqual(contest.get_start_time().day, 13)
        self.assertEqual(contest.get_duration().total_seconds(), 2 * 60 * 60)
        self.assertEqual(contest.get_can_participate(), 'All')
        self.assertEqual(contest.get_rated_range(), ' ~ 2799')
        self.assertEqual(contest.get_penalty().total_seconds(), 5 * 60)

        contest = AtCoderContest.from_url('https://atcoder.jp/contests/dp')
        self.assertEqual(contest.get_name(lang='ja'), 'Educational DP Contest / DP まとめコンテスト')
        self.assertEqual(contest.get_name(lang='en'), 'Educational DP Contest')
        self.assertEqual(contest.get_start_time().year, 2019)
        self.assertEqual(contest.get_start_time().month, 1)
        self.assertEqual(contest.get_start_time().day, 6)
        self.assertEqual(contest.get_duration().total_seconds(), 5 * 60 * 60)
        self.assertEqual(contest.get_can_participate(), 'All')
        self.assertEqual(contest.get_rated_range(), '-')
        self.assertEqual(contest.get_penalty().total_seconds(), 5 * 60)

    def test_get_penalty_a_singular_form(self):
        contest = AtCoderContest.from_url('https://atcoder.jp/contests/chokudai_S002')
        self.assertEqual(contest.get_penalty().total_seconds(), 60)  # Penalty is written as "1 minute", not  "1 minutes"

    def test_list_problems(self):
        contest = AtCoderContest.from_url('https://atcoder.jp/contests/agc028')
        problems = contest.list_problems()
        self.assertEqual(len(problems), 7)
        self.assertEqual(problems[0].get_alphabet(), 'A')
        self.assertEqual(problems[0].get_name(), 'Two Abbreviations')
        self.assertEqual(problems[0].get_time_limit_msec(), 2000)
        self.assertEqual(problems[0].get_memory_limit_byte(), 1024 * 1000 * 1000)
        self.assertEqual(problems[5].get_alphabet(), 'F')
        self.assertEqual(problems[5].problem_id, 'agc028_f')
        self.assertEqual(problems[6].get_alphabet(), 'F2')
        self.assertEqual(problems[6].problem_id, 'agc028_f2')

    def test_list_problems_with_float_values(self):
        """
        .. seealso:
            https://github.com/kmyk/online-judge-tools/issues/412
        """

        contest = AtCoderContest.from_url('https://atcoder.jp/contests/dwacon2018-final-open')
        problems = contest.list_problems()
        self.assertEqual(problems[0].get_time_limit_msec(), 2525)
        self.assertEqual(problems[0].get_memory_limit_byte(), int(252.525 * 1000 * 1000))
        self.assertEqual(problems[1].get_time_limit_msec(), 5252)
        self.assertEqual(problems[1].get_memory_limit_byte(), int(525.252 * 1000 * 1000))

    def test_list_problems_time_limit_is_less_than_msec(self):
        contest = AtCoderContest.from_url('https://atcoder.jp/contests/joi2019ho')
        problems = contest.list_problems()
        self.assertEqual(problems[0].get_time_limit_msec(), 1000)
        self.assertEqual(problems[1].get_time_limit_msec(), 1000)
        self.assertEqual(problems[2].get_time_limit_msec(), 500)
        self.assertEqual(problems[3].get_time_limit_msec(), 1000)
        self.assertEqual(problems[4].get_time_limit_msec(), 2000)

    def test_list_problems_memory_limit_is_zero(self):
        contest = AtCoderContest.from_url('https://atcoder.jp/contests/future-contest-2019-final-open')
        problems = contest.list_problems()
        self.assertEqual(problems[0].get_memory_limit_byte(), 1024 * 1000 * 1000)  # 1024 MB
        self.assertEqual(problems[1].get_memory_limit_byte(), 0)  # 0 KB

    def test_iterate_submissions(self):
        contest = AtCoderContest.from_url('https://atcoder.jp/contests/code-festival-2014-exhibition-open')
        submissions = list(contest.iterate_submissions())
        self.assertGreater(len(submissions), 300)
        self.assertEqual(submissions[0].get_code_size(), 276)
        self.assertEqual(submissions[0].get_status(), 'WA')
        self.assertEqual(submissions[1].get_user_id(), 'snuke')
        self.assertEqual(submissions[1].get_status(), 'WA')


class AtCoderProblemTest(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(AtCoderProblem.from_url('https://kupc2014.contest.atcoder.jp/tasks/kupc2014_d').contest_id, 'kupc2014')
        self.assertEqual(AtCoderProblem.from_url('https://kupc2014.contest.atcoder.jp/tasks/kupc2014_d').problem_id, 'kupc2014_d')
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/agc030/tasks/agc030_c').contest_id, 'agc030')
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/agc030/tasks/agc030_c').problem_id, 'agc030_c')

    def test_repr(self):
        self.assertEqual(repr(AtCoderProblem('kupc2014', 'kupc2014_d')), "AtCoderProblem.from_url('https://atcoder.jp/contests/kupc2014/tasks/kupc2014_d')")
        self.assertEqual(repr(AtCoderProblem('agc030', 'agc030_c')), "AtCoderProblem.from_url('https://atcoder.jp/contests/agc030/tasks/agc030_c')")
        self.assertEqual(repr(AtCoderProblem('xxxxxx', 'yyyyyy')), "AtCoderProblem.from_url('https://atcoder.jp/contests/xxxxxx/tasks/yyyyyy')")

    def test_eq(self):
        self.assertEqual(AtCoderProblem.from_url('https://kupc2014.contest.atcoder.jp/tasks/kupc2014_d'), AtCoderProblem.from_url('https://atcoder.jp/contests/kupc2014/tasks/kupc2014_d'))
        self.assertNotEqual(AtCoderProblem.from_url('https://kupc2014.contest.atcoder.jp/tasks/kupc2014_d'), AtCoderProblem.from_url('https://atcoder.jp/contests/agc030/tasks/agc030_c'))

    def test_load_details(self):
        problem = AtCoderProblem.from_url('https://atcoder.jp/contests/abc118/tasks/abc118_a')
        self.assertEqual(problem.get_alphabet(), 'A')
        self.assertEqual(problem.get_name(), 'B +/- A')
        self.assertEqual(problem.get_time_limit_msec(), 2000)
        self.assertEqual(problem.get_memory_limit_byte(), 1024 * 1000 * 1000)
        self.assertEqual(problem.get_score(), 100)

    def test_get_alphabet(self):
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/agc028/tasks/agc028_f').get_alphabet(), 'F')
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/agc028/tasks/agc028_f2').get_alphabet(), 'F2')

    def test_get_score(self):
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/future-contest-2018-final/tasks/future_contest_2018_final_a').get_score(), 50000000)
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/abc001/tasks/abc001_4').get_score(), None)

    def test_get_score_latex(self):
        """
        .. seealso::
            https://github.com/kmyk/online-judge-tools/issues/411
        """

        self.assertIsNone(AtCoderProblem.from_url('https://atcoder.jp/contests/wupc2019/tasks/wupc2019_a').get_score())

    def test_get_time_limit_is_less_than_msec(self):
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/joi2019ho/tasks/joi2019ho_c').get_time_limit_msec(), 500)
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/future-contest-2019-qual/tasks/future_contest_2019_qual_b').get_time_limit_msec(), 0)

    def test_get_memory_limit_is_zero(self):
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/future-contest-2019-qual/tasks/future_contest_2019_qual_b').get_memory_limit_byte(), 0)

    def test_iterate_submissions(self):
        problem = AtCoderProblem.from_url('https://atcoder.jp/contests/abc119/tasks/abc119_c')
        submissions = problem.iterate_submissions()
        self.assertEqual(next(submissions).get_score(), 300)
        self.assertEqual(next(submissions).get_code_size(), 1208)
        self.assertEqual(next(submissions).get_exec_time_msec(), 2)
        self.assertEqual(next(submissions).get_memory_byte(), 256 * 1000)


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
        self.assertEqual(submission.get_status(), 'AC')
        self.assertEqual(submission.get_exec_time_msec(), 85)
        self.assertEqual(submission.get_memory_byte(), 3328 * 1000)

    def test_submission_info_compile_error(self):
        submission = AtCoderSubmission.from_url('https://atcoder.jp/contests/abc124/submissions/4943518')
        self.assertEqual(submission.get_submission_time().year, 2019)
        self.assertEqual(submission.get_submission_time().month, 4)
        self.assertEqual(submission.get_submission_time().day, 13)
        self.assertEqual(submission.get_user_id(), 'pekempey')
        self.assertEqual(submission.get_problem().problem_id, 'abc124_d')
        self.assertEqual(submission.get_language_name(), 'Rust (1.15.1)')
        self.assertEqual(submission.get_score(), 0)
        self.assertEqual(submission.get_code_size(), 787)
        self.assertEqual(submission.get_status(), 'CE')
        self.assertEqual(submission.get_exec_time_msec(), None)
        self.assertEqual(submission.get_memory_byte(), None)

    def test_submission_info_compile_warnings(self):
        submission = AtCoderSubmission.from_url('https://atcoder.jp/contests/agc032/submissions/4675493')
        self.assertEqual(submission.get_submission_time().year, 2019)
        self.assertEqual(submission.get_submission_time().month, 3)
        self.assertEqual(submission.get_submission_time().day, 23)
        self.assertEqual(submission.get_user_id(), 'yutaka1999')
        self.assertEqual(submission.get_problem().problem_id, 'agc032_e')
        self.assertEqual(submission.get_language_name(), 'C++14 (GCC 5.4.1)')
        self.assertEqual(submission.get_score(), 0)
        self.assertEqual(submission.get_code_size(), 1682)
        self.assertEqual(submission.get_status(), 'WA')
        self.assertEqual(submission.get_exec_time_msec(), 392)
        self.assertEqual(submission.get_memory_byte(), 7168 * 1000)

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

    def test_get_score_float(self):
        submission = AtCoderSubmission.from_url('https://atcoder.jp/contests/pakencamp-2018-day3/submissions/4583531')
        self.assertAlmostEqual(submission.get_score(), 32.53)


class AtCoderProblemContentTest(unittest.TestCase):
    def test_from_html(self):
        url = 'https://atcoder.jp/contests/abc114/tasks/abc114_d'
        resp = requests.get(url)
        html = resp.content.decode(resp.apparent_encoding)
        content = AtCoderProblemContent.from_html(html, problem=AtCoderProblem.from_url(url))

        self.assertEqual(content.alphabet, 'D')
        self.assertEqual(content.available_languages, None)
        self.assertEqual(content.html, html)
        self.assertEqual(content.input_format, '<var>N</var>\r\n')
        self.assertEqual(content.memory_limit_byte, 1024 * 1000 * 1000)
        self.assertEqual(content.name, '756')
        self.assertEqual(content.problem, AtCoderProblem.from_url(url))
        self.assertEqual(content.sample_cases, [
            TestCase(name='sample-1', input_name='入力例 1', input_data=b'9\n', output_name='出力例 1', output_data=b'0\n'),
            TestCase(name='sample-2', input_name='入力例 2', input_data=b'10\n', output_name='出力例 2', output_data=b'1\n'),
            TestCase(name='sample-3', input_name='入力例 3', input_data=b'100\n', output_name='出力例 3', output_data=b'543\n'),
        ])
        self.assertEqual(content.score, 400)
        self.assertEqual(content.time_limit_msec, 2 * 1000)


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

        self.assertEqual(AtCoderProblem.from_url('https://beta.atcoder.jp/contests/agc001/tasks/agc001_d').get_input_format(), '<var>N</var> <var>M</var>\r\n<var>A_1</var> <var>A_2</var> <var>...</var> <var>A_M</var>\r\n')
        self.assertEqual(AtCoderProblem.from_url('https://beta.atcoder.jp/contests/agc002/tasks/agc002_d').get_input_format(), '\r\n<var>N</var> <var>M</var>\r\n<var>a_1</var> <var>b_1</var>\r\n<var>a_2</var> <var>b_2</var>\r\n<var>:</var>\r\n<var>a_M</var> <var>b_M</var>\r\n<var>Q</var>\r\n<var>x_1</var> <var>y_1</var> <var>z_1</var>\r\n<var>x_2</var> <var>y_2</var> <var>z_2</var>\r\n<var>:</var>\r\n<var>x_Q</var> <var>y_Q</var> <var>z_Q</var>\r\n')
        self.assertEqual(AtCoderProblem.from_url('https://beta.atcoder.jp/contests/agc003/tasks/agc003_d').get_input_format(), '<var>N</var>\r\n<var>s_1</var>\r\n:\r\n<var>s_N</var>\r\n')
        self.assertEqual(AtCoderProblem.from_url('https://beta.atcoder.jp/contests/agc004/tasks/agc004_d').get_input_format(), '<var>N</var> <var>K</var>\r\n<var>a_1</var> <var>a_2</var> <var>...</var> <var>a_N</var>\r\n')
        self.assertEqual(AtCoderProblem.from_url('https://beta.atcoder.jp/contests/agc005/tasks/agc005_d').get_input_format(), '<var>N</var> <var>K</var>\r\n')

        self.assertEqual(AtCoderProblem.from_url('https://beta.atcoder.jp/contests/arc083/tasks/arc083_a').get_input_format(), '<var>A</var> <var>B</var> <var>C</var> <var>D</var> <var>E</var> <var>F</var>\r\n')

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

        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/arc001/tasks/arc001_1').get_input_format(), '\r\n<var>N</var>\r\n<var>c_1c_2c_3…c_N</var>\r\n')
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/arc002/tasks/arc002_3').get_input_format(), '\r\n<var>N</var>\r\n<var>c_{1}c_{2}...c_{N}</var>\r\n')
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/arc034/tasks/arc034_4').get_input_format(), '\r\n<var>A</var> <var>B</var> <var>C</var>\r\n<var>a_1</var> <var>a_2</var> .. <var>a_A</var>\r\n<var>b_1</var> <var>b_2</var> .. <var>b_B</var>\r\n')

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

        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/dwacon2018-final/tasks/dwacon2018_final_a').get_input_format(), '\r\n<var>H</var> <var>M</var> <var>S</var>\r\n<var>C_1</var> <var>C_2</var>\r\n')
        self.assertEqual(AtCoderProblem.from_url('https://atcoder.jp/contests/dwacon2018-final/tasks/dwacon2018_final_b').get_input_format(), '\r\n<var>N</var> <var>K</var>\r\n<var>v_1</var> <var>...</var> <var>v_N</var>\r\n')

    def test_problem_without_input(self):
        self.assertIsNone(AtCoderProblem.from_url('https://atcoder.jp/contests/tenka1-2013-quala/tasks/tenka1_2013_qualA_a').get_input_format())

    def test_problem_without_input_format(self):
        self.assertIsNone(AtCoderProblem.from_url('https://atcoder.jp/contests/joi2006ho/tasks/joi2006ho_a').get_input_format())


if __name__ == '__main__':
    unittest.main()
