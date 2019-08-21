import os
import unittest

import onlinejudge._implementation.utils as utils
from onlinejudge.service.topcoder import TopcoderLongContestProblem, TopcoderService


class TopcoderSerivceTest(unittest.TestCase):
    def test_from_url(self):
        self.assertIsInstance(TopcoderService.from_url('https://community.topcoder.com/'), TopcoderService)
        self.assertIsNone(TopcoderService.from_url('https://atcoder.jp/'))


class TopcoderLongConrestProblemTest(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(TopcoderLongContestProblem.from_url('https://community.topcoder.com/longcontest/?module=ViewProblemStatement&rd=17092&pm=14853').rd, 17092)
        self.assertEqual(TopcoderLongContestProblem.from_url('https://community.topcoder.com/longcontest/?module=ViewProblemStatement&rd=17092&pm=14853').pm, 14853)

    # TODO: write a mock test
    def test_download_standings_expired(self):
        problem = TopcoderLongContestProblem.from_url('https://community.topcoder.com/longcontest/?module=ViewProblemStatement&rd=17143&pm=14889')
        self.assertRaises(Exception, problem.download_standings)

    def test_download_overview(self):
        problem = TopcoderLongContestProblem.from_url('https://community.topcoder.com/longcontest/?module=ViewProblemStatement&rd=17143&pm=14889')
        overview = problem.download_overview()
        self.assertEqual(len(overview), 282)
        self.assertEqual(overview[4].rank, 5)
        self.assertEqual(overview[4].handle, 'hakomo')
        self.assertEqual(overview[4].provisional_rank, 6)
        self.assertAlmostEqual(overview[4].provisional_score, 812366.55)
        self.assertAlmostEqual(overview[4].final_score, 791163.70)
        self.assertEqual(overview[4].language, 'C++')
        self.assertEqual(overview[4].cr, 22924522)

    def test_download_individual_results_feed(self):
        problem = TopcoderLongContestProblem.from_url('https://community.topcoder.com/longcontest/?module=ViewProblemStatement&rd=17143&pm=14889')
        cr = 22924522
        feed = problem.download_individual_results_feed(cr=cr)
        self.assertEqual(feed.round_id, problem.rd)
        self.assertEqual(feed.coder_id, cr)
        self.assertEqual(feed.handle, 'hakomo')
        self.assertEqual(feed.submissions[0].number, 1)
        self.assertAlmostEqual(feed.submissions[0].score, 816622.81)
        self.assertEqual(feed.submissions[0].language, 'C++')
        self.assertEqual(feed.submissions[0].time, '04/22/2018 09:56:48')
        self.assertEqual(feed.testcases[0].test_case_id, 33800773)
        self.assertAlmostEqual(feed.testcases[0].score, 1.0)
        self.assertEqual(feed.testcases[0].processing_time, 164)
        self.assertEqual(feed.testcases[0].fatal_error_ind, 0)
        self.assertEqual(len(feed.submissions), 5)
        self.assertEqual(len(feed.testcases), 2000)

    @unittest.skipIf('CI' in os.environ, 'login is required')
    def test_download_system_test(self):
        with utils.with_cookiejar(utils.get_default_session()):
            url = 'https://community.topcoder.com/longcontest/?module=ViewProblemStatement&rd=17143&pm=14889'
            tid = 33800773
            problem = TopcoderLongContestProblem.from_url(url)
            self.assertEqual(problem.download_system_test(tid), 'seed = 1919427468645\nH = 85\nW = 88\nC = 2\n')

        with utils.with_cookiejar(utils.get_default_session()):
            url = 'https://community.topcoder.com/longcontest/?module=ViewProblemStatement&rd=17092&pm=14853'
            tid = 33796324
            problem = TopcoderLongContestProblem.from_url(url)
            self.assertEqual(problem.download_system_test(tid), """\
Seed = 2917103922548

Coins: 5372
Max Time: 2988
Note Time: 5
Num Machines: 3

Machine 0...
Wheel 0: ACEEDEDBDGBADCDFGD
Wheel 1: GGFEFBFDFFDEECFEAG
Wheel 2: EFCCCAADBDGEGBDCDD
Expected payout rate: 1.5775034293552812

Machine 1...
Wheel 0: CDFFDEEEAGGGGGFGGBEFCCFFFD
Wheel 1: EDCGBGFBBCCGGFGDFBFECGGEFC
Wheel 2: GEDECEGFDCGDGGCDDCEDGBGEBG
Expected payout rate: 0.7345243513882568

Machine 2...
Wheel 0: ABEEDDDCGBG
Wheel 1: EDEEDADGEAF
Wheel 2: EBEGEFEGEBF
Expected payout rate: 0.6160781367392938

""")
