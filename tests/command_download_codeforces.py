import os
import unittest

import tests.command_download


class DownloadCodeforcesTest(unittest.TestCase):
    def snippet_call_download(self, *args, **kwargs):
        tests.command_download.snippet_call_download(self, *args, **kwargs)

    def test_call_download_codeforces_problemset_700_b(self):
        self.snippet_call_download('http://codeforces.com/problemset/problem/700/B', {
            'sample-1.in': '1f38b0f27f4b0005e5409e834ff59166',
            'sample-2.out': '7c5aba41f53293b712fd86d08ed5b36e',
            'sample-2.in': '8a8c08b2901d4cfca41ad0703dfa718e',
            'sample-1.out': '9ae0ea9e3c9c6e1b9b6252c8395efdc1',
        })

    def test_call_download_codeforces_contest_538_h(self):
        self.snippet_call_download('http://codeforces.com/contest/538/problem/H', {
            'sample-1.in': 'c8483ca371b414e911ccbecf239beed6',
            'sample-2.out': '87a45b8adc25c7bf37eaa25b530de79c',
            'sample-2.in': 'afa0c8b2336e798b5f29a200a18432d1',
            'sample-1.out': '166a3645f3c31595526624ce003b41fc',
        })

    def test_call_download_codeforces_gym_101021_a(self):
        self.snippet_call_download('http://codeforces.com/gym/101021/problem/A', {
            'sample-1.in': '4dfb06c20503a3f0dbe0fb29dd52d304',
            'sample-2.out': '614a0c8025f8bbcf46b8ba0ff9fd61d1',
            'sample-2.in': 'dcfe1f14721a0e141c2e31adeebe7a53',
            'sample-1.out': '45778e8e2d350841cf68711ece5cb9e1',
        })

    def test_call_download_codeforces_contest_1080_a(self):
        self.snippet_call_download('https://codeforces.com/contest/1080/problem/A', {
            'sample-1.in': '54d3363c78b5001b1a6f382f47e08b60',
            'sample-1.out': '31d30eea8d0968d6458e0ad0027c9f80',
            'sample-2.in': 'd33b56dd139d846a5df6eab7cfaf83e8',
            'sample-2.out': 'bda81ba88c634b46394ead43aff31ad5',
        })
