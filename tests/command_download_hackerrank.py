import unittest

import tests.command_download


class DownloadHackerRankTest(unittest.TestCase):
    def snippet_call_download(self, *args, **kwargs):
        tests.command_download.snippet_call_download(self, *args, **kwargs)

    def test_call_download_hackerrank_beautiful_array(self):
        self.snippet_call_download('https://www.hackerrank.com/contests/hourrank-1/challenges/beautiful-array', {
            'sample-1.in': 'fb3f7e56dac548ce73f9d8e485e5336b',
            'sample-2.out': '897316929176464ebc9ad085f31e7284',
            'sample-2.in': '6047a07c8defde4d696513d26e871b20',
            'sample-1.out': '6d7fce9fee471194aa8b5b6e47267f03',
        })
