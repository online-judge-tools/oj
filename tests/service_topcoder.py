import unittest

from onlinejudge.service.topcoder import TopcoderLongContestProblem, TopcoderService


class TopcoderSerivceTest(unittest.TestCase):
    def test_from_url(self):
        self.assertIsInstance(TopcoderService.from_url('https://community.topcoder.com/'), TopcoderService)
        self.assertIsNone(TopcoderService.from_url('https://atcoder.jp/'))


class TopcoderLongConrestProblemTest(unittest.TestCase):
    def test_from_url(self):
        self.assertEqual(TopcoderLongContestProblem.from_url('https://community.topcoder.com/longcontest/?module=ViewProblemStatement&rd=17092&pm=14853').rd, 17092)
        self.assertEqual(TopcoderLongContestProblem.from_url('https://community.topcoder.com/longcontest/?module=ViewProblemStatement&rd=17092&pm=14853').pm, 14853)

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
        feed = problem.download_individual_results_feed(cr)
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
