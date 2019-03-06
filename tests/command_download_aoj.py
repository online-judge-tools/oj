import os
import unittest

import tests.command_download


class DownloadAOJTest(unittest.TestCase):
    def snippet_call_download(self, *args, **kwargs):
        tests.command_download.snippet_call_download(self, *args, **kwargs)

    def test_call_download_aoj_DSL_1_A(self):
        self.snippet_call_download('http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=DSL_1_A', {
            'sample-1.in': 'cb3a243a13637cddedf245cd0f6eab86',
            'sample-1.out': '29cc7a34bb5a15da3d14ef4a82a4c530',
        })

    def test_call_download_aoj_0100(self):
        self.snippet_call_download('http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=0100', {
            'sample-1.in': '4f0f7b3b0b73c97c5283395edde3dbe8',
            'sample-1.out': '26d3b085a160c028485f3865d07b9192',
        })

    def test_call_download_aoj_1371(self):
        self.snippet_call_download('http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=1371', {
            'sample-6.in': '3521658c02c291ad5a4e5cbaa3cb0260',
            'sample-2.out': 'b026324c6904b2a9cb4b88d6d61c81d1',
            'sample-3.in': 'b9775d52323c110b406d53b9805cee01',
            'sample-3.out': '6d7fce9fee471194aa8b5b6e47267f03',
            'sample-1.out': '897316929176464ebc9ad085f31e7284',
            'sample-5.in': '0b06c70869a30733379a72e2a8c03758',
            'sample-4.out': 'b026324c6904b2a9cb4b88d6d61c81d1',
            'sample-7.out': '897316929176464ebc9ad085f31e7284',
            'sample-6.out': 'b026324c6904b2a9cb4b88d6d61c81d1',
            'sample-5.out': '897316929176464ebc9ad085f31e7284',
            'sample-2.in': 'f3c536f039be83a4ef0e8f026984d87d',
            'sample-1.in': '56092c4794d713f93d2bb70a66aa6ca1',
            'sample-4.in': '318d4b3abfa30cc8fad4b1d34430aea3',
            'sample-7.in': 'dcac31a5a6542979ce45064ab0bfa83d',
        })

    def test_call_download_aoj_2256(self):
        self.snippet_call_download('http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=2256&lang=jp', {
            'sample-1.in': 'c89817f1ee0b53209d66abc94e457f7f',
            'sample-1.out': 'b9c2c5761360aad068453f4e64dd5a4e',
        })

    def test_call_download_aoj_2310(self):
        self.snippet_call_download('http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=2310&lang=jp', {
            'sample-1.in': '27ed9e879684b438fa6cc80c4261daf7',
            'sample-1.out': '48a24b70a0b376535542b996af517398',
            'sample-2.in': 'bb84849858ca512e14e071e25120ed78',
            'sample-2.out': '6d7fce9fee471194aa8b5b6e47267f03',
            'sample-3.in': '4c4ae7fb491ec5c6ad57d9d5711e44a6',
            'sample-3.out': '9ae0ea9e3c9c6e1b9b6252c8395efdc1',
            'sample-4.in': 'ad1109594a97eabe9bee60a743006de7',
            'sample-4.out': '84bc3da1b3e33a18e8d5e1bdd7a18d7a',
            'sample-5.in': 'b80447e0bc0c4ecc6fb3001b6a4e79f6',
            'sample-5.out': 'c30f7472766d25af1dc80b3ffc9a58c7',
        })

    def test_call_download_aoj_2511(self):
        self.snippet_call_download('http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=2511', {
            'sample-1.in': '0483a0080de977d5e1db1ab87eae3fa9',
            'sample-1.out': '346ce6367eff6bb3c9915601f2ae1e75',
        })

    def test_call_download_aoj_DSL_3_B(self):
        self.snippet_call_download('https://onlinejudge.u-aizu.ac.jp/courses/library/3/DSL/3/DSL_3_B', {
            'sample-1.in': '36adbcbb268e04ef7667fb2d965eed2c',
            'sample-1.out': '26ab0db90d72e28ad0ba1e22ee510510',
            'sample-2.in': '89a4280a03ec0001ec91f3fedbafadc1',
            'sample-2.out': '6d7fce9fee471194aa8b5b6e47267f03',
            'sample-3.in': '22d823cf994ebee157a0cdc8219a600d',
            'sample-3.out': '897316929176464ebc9ad085f31e7284',
        })

    def test_call_download_aoj_2394(self):
        self.snippet_call_download('https://onlinejudge.u-aizu.ac.jp/challenges/sources/JAG/Spring/2394?year=2011', {
            'sample-1.in': '05dfaf25ae93e601a10cfb278db7679c',
            'sample-1.out': '80982df7f6dac58f828e2e8b12e87a0a',
        })

    def test_call_download_aoj_system_ITP1_1_B(self):
        self.snippet_call_download(
            'http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=ITP1_1_B', {
                'test1.in': 'b026324c6904b2a9cb4b88d6d61c81d1',
                'test1.out': 'b026324c6904b2a9cb4b88d6d61c81d1',
                'test2.in': '6d7fce9fee471194aa8b5b6e47267f03',
                'test2.out': '66a7c1d5cb75ef2542524d888fd32f4a',
                'test3.in': '9caff0735bc6e80121cedcb98ca51821',
                'test3.out': 'fef5f767008b27f5c3801382264f46ef',
                'test4.in': '919d117956d3135c4c683ff021352f5c',
                'test4.out': 'b39ffd5aa5029d696193c8362dcb1d19',
            }, is_system=True)

    def test_call_download_aoj_system_1169(self):
        # NOTE: the data exists, but AOJ says "..... (terminated because of the limitation)"
        self.snippet_call_download(
            'http://judge.u-aizu.ac.jp/onlinejudge/description.jsp?id=1169&lang=jp',
            {
                # '1.in':  'f0ecaede832a038d0e940c2c4d0ab5e5',
                # '1.out': '8d2f7846dc2fc10ef37dcb548635c788',
            },
            is_system=True)
