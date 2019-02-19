import unittest

import tests.command_download


class DownloadHackerRankTest(unittest.TestCase):
    def snippet_call_download(self, *args, **kwargs):
        tests.command_download.snippet_call_download(self, *args, **kwargs)

    # TODO: support parsing HTML or retrieving from "Run Code" feature
    @unittest.skip('the "Download all test cases" feature is not supported for this problem')
    def test_call_download_hackerrank_beautiful_array(self):
        self.snippet_call_download('https://www.hackerrank.com/contests/hourrank-1/challenges/beautiful-array', {
            'sample-1.in': 'fb3f7e56dac548ce73f9d8e485e5336b',
            'sample-2.out': '897316929176464ebc9ad085f31e7284',
            'sample-2.in': '6047a07c8defde4d696513d26e871b20',
            'sample-1.out': '6d7fce9fee471194aa8b5b6e47267f03',
        })

    def test_call_download_hackerrank_hourrank_30_a_system(self):
        self.snippet_call_download(
            'https://www.hackerrank.com/contests/hourrank-30/challenges/video-conference', {
                '00.in': 'b138a1282e79697057d5eca993a29414',
                '00.out': 'de044533ac6d30ed89eb5b4e10ff105b',
                '01.in': '0e64d38accc35d4b8ac4fc0df3b5b969',
                '01.out': '3362cf9066bba541387e5b6787b13e6e',
                '02.in': '7df575910d94fecb93861eaf414d86dd',
                '02.out': 'eb68db6a13e73b093d620f865e4cc098',
                '03.in': 'd87880f0cd02ee106a8cadc5ccd97ed0',
                '03.out': 'a24f9580a3701064cb49534689b50b60',
                '04.in': 'f5981eb3068da7d2d2c1b84b23ea8710',
                '04.out': 'df0a3dfc2217cbc8e8828e423933206b',
                '05.in': 'b1387e51b1f9c4e16713647b36e8341b',
                '05.out': 'ac14c5fed571104401167dd04fdcf417',
                '06.in': 'ba080fc7b89b2aed00fcf03a5db29f8a',
                '06.out': '3a365fc4aec7cad9536c598b7d892e7a',
                '07.in': '9d3f2cfb7b6412ef40a8b5ef556c3a46',
                '07.out': '8e7a02d5c6bdd9358c589b3e400bacb8',
                '08.in': '8409f37413e40f3baee0314bcacfc0a4',
                '08.out': 'fe2d333498a3bdebaa0f4c88803566ff',
                '09.in': '6f3e4c84441ae56e141a600542cc8ec8',
                '09.out': '66e67dc4e8edbf66ed9ae2c9a0862f2b',
                '10.in': 'fe24b76ea70e0a44213d7f22d183a33b',
                '10.out': '8b8ba206ea7bbb02f0361341cb8da7c7',
            }, is_system=True, is_silent=True)
