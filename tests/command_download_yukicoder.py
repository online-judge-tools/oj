import unittest

import tests.command_download
from onlinejudge_workaround_for_conflict.service.yukicoder import YukicoderService


class DownloadYukicoderTest(unittest.TestCase):
    def snippet_call_download(self, *args, **kwargs):
        tests.command_download.snippet_call_download(self, *args, **kwargs)

    def test_call_download_yukicoder_100(self):
        self.snippet_call_download('http://yukicoder.me/problems/100', {
            'sample-3.out': '63a98316f78c5127e702db8fbea612a6',
            'sample-2.in': '3b6feb4b7d767c8e7314f59a1749d544',
            'sample-2.out': '9f4c0b1fca5cb6f886aa2e54442b1e1b',
            'sample-3.in': 'c12ec911666a5d65bf53e234291e402c',
            'sample-1.in': 'c8a8eeb947c8a1d6700d6f7fd151cb00',
            'sample-1.out': '3bb50ff8eeb7ad116724b56a820139fa',
        })

    @unittest.skipIf(not tests.utils.is_logged_in(YukicoderService()), 'login is required')
    def test_call_download_yukicoder_no_8_system(self):
        self.snippet_call_download('https://yukicoder.me/problems/no/8', {
            '01.txt.in': '04e90eb0c4a65eefa084dfea8e89de9f',
            '01.txt.out': 'fc07e56c1012af450b912af02f1e7c30',
            '02.txt.in': 'e867414a12769d8adc9086093620b4a3',
            '02.txt.out': '92289ff0469cfacb19a2809e6b44b93a',
            '03.txt.in': 'c15d6580553f2be2c4b133441da760f3',
            '03.txt.out': '5ff2d623f9ec55b7207a0e15f076a511',
            '04.txt.in': 'e28f58da56e572f4f27f9b837a4fe8c5',
            '04.txt.out': 'b9d27fd37514d704abe776e239029fae',
            '05.txt.in': 'd04e3cd98784a870b8dae31ab8e2c935',
            '05.txt.out': '559ffd2e020994c7117fdc38da1dd97d',
            '06.txt.in': '897059f9374e64ed03e09a5b5044794c',
            '06.txt.out': 'a3d50a58dc67267b5e4619ecf73b2dcc',
            '07.txt.in': '69d224c83e03e0c3f6ff466fa06bc7dc',
            '07.txt.out': 'a3d50a58dc67267b5e4619ecf73b2dcc',
            '08.txt.in': 'de61c37c042526933ac9ff5c99dd8681',
            '08.txt.out': 'a3d50a58dc67267b5e4619ecf73b2dcc',
            '09.txt.in': 'b627b556c53cb20b9ae8fa4665925aa9',
            '09.txt.out': 'a3d50a58dc67267b5e4619ecf73b2dcc',
            '10.txt.in': '735f5246a7bde15f85ae368917eee087',
            '10.txt.out': 'a3d50a58dc67267b5e4619ecf73b2dcc',
            '99_system_test1.txt.in': '1e5aa1c7ed5de43807f7ceae3ab60b82',
            '99_system_test1.txt.out': '03a0df412a4b34652f3ef094e6dd4eda',
        }, is_system=True)
