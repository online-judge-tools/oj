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
