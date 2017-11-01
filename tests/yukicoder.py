# -*- coding: utf-8 -*-
import unittest

from onlinejudge.yukicoder import YukicoderService

class YukicoderTest(unittest.TestCase):

    def test_get_user_10(self):
        data = YukicoderService().get_user(id=10)
        self.assertEqual(data['Id'], 10)
        self.assertEqual(data['Name'], 'yuki2006')
    def test_get_user_yuki2006(self):
        data = YukicoderService().get_user(name='yuki2006')
        self.assertEqual(data['Id'], 10)
        self.assertEqual(data['Name'], 'yuki2006')
    def test_get_user_0(self):
        data = YukicoderService().get_user(id=0)
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
        self.assertAlmostEqual(it['レベル'], 1.5)

    def test_get_user_favorite_wiki_10(self):
        data = YukicoderService().get_user_favorite_wiki(id=10)
        it = list(filter(lambda row: row['Wikiページ'] == 'decomposable_searching_problem', data))
        self.assertEqual(len(it), 1)

    def test_get_submissions(self):
        data = YukicoderService().get_submissions(page=3, status='TLE')
        self.assertEqual(len(data), 50)
        self.assertEqual(data[4]['結果'], 'TLE')

if __name__ == '__main__':
    unittest.main()
