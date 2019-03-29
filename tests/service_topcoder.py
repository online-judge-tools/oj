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
