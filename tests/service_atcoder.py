# -*- coding: utf-8 -*-
import unittest

from onlinejudge.service.atcoder import AtCoderService


class AtCoderSerivceTest(unittest.TestCase):
    def test_from_url(self):
        service = AtCoderService()
        self.assertEqual(AtCoderService.from_url('https://atcoder.jp/'), service)
        self.assertEqual(AtCoderService.from_url('https://beta.atcoder.jp/'), service)
        self.assertEqual(AtCoderService.from_url('https://abc001.contest.atcoder.jp/'), service)
        self.assertEqual(AtCoderService.from_url('https://atcoder.jp/contests/agc001/submissions/806160'), service)
        self.assertEqual(AtCoderService.from_url('https://codeforces.com/'), None)

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
        self.assertEqual(contest.get_contest_name(), '東京大学プログラミングコンテスト2013')
        self.assertEqual(contest.get_duration().total_seconds(), 5 * 60 * 60)
        self.assertEqual(contest.get_rated_range(), 'All')


if __name__ == '__main__':
    unittest.main()
