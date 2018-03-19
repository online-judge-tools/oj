import unittest
import tests.download

import os

class DownloadYukicoderTest(unittest.TestCase):

    def snippet_call_download(self, *args, **kwargs):
        tests.download.snippet_call_download(self, *args, **kwargs)

    def test_call_download_yukicoder_no_9002(self):
        self.snippet_call_download(
            'http://yukicoder.me/problems/no/9002', {
                'sample-1.in':  'b026324c6904b2a9cb4b88d6d61c81d1',
                'sample-2.out': 'a403d4dbee7bd783539da3efa43c4399',
                'sample-2.in':  '5b6b41ed9b343fed9cd05a66d36650f0',
                'sample-1.out': 'b026324c6904b2a9cb4b88d6d61c81d1',
            })
    def test_call_download_yukicoder_100(self):
        self.snippet_call_download(
            'http://yukicoder.me/problems/100', {
                'sample-3.out': '63a98316f78c5127e702db8fbea612a6',
                'sample-2.in':  '3b6feb4b7d767c8e7314f59a1749d544',
                'sample-2.out': '9f4c0b1fca5cb6f886aa2e54442b1e1b',
                'sample-3.in':  'c12ec911666a5d65bf53e234291e402c',
                'sample-1.in':  'c8a8eeb947c8a1d6700d6f7fd151cb00',
                'sample-1.out': '3bb50ff8eeb7ad116724b56a820139fa',
            })
    def test_call_download_yukicoder_no_104(self):
        self.snippet_call_download(
            'http://yukicoder.me/problems/no/104', {
                'sample-3.out': '89c2e8d24975544fd508992593bd4556',
                'sample-2.in':  '82e80aeb6240ed14d8a0f8df1bc4ab19',
                'sample-2.out': '2737b49252e2a4c0fe4c342e92b13285',
                'sample-3.in':  '802bd42d2ee2af1b0f2165ba526bd1f8',
                'sample-1.in':  'bc6bccbab69279fd7c28fc71654e57bc',
                'sample-4.in':  '68b329da9893e34099c7d8ad5cb9c940',
                'sample-1.out': '1dcca23355272056f04fe8bf20edfce0',
                'sample-4.out': 'b026324c6904b2a9cb4b88d6d61c81d1',
            })
    def test_call_download_yukicoder_no_400(self):
        self.snippet_call_download(
            'http://yukicoder.me/problems/no/400', {
                'sample-3.out': '9c9eb7aca96d568294f752ecd6867cbe',
                'sample-2.in':  '60650122d9941f5b816451ca15d9eff9',
                'sample-2.out': '90e2a41ae5ea1f30688dcf72ba806b17',
                'sample-3.in':  '9c9eb7aca96d568294f752ecd6867cbe',
                'sample-1.in':  '04b3f6b553cb51fcc486e0a8888c79eb',
                'sample-4.in':  '787786577e5cb219fd38409b5cb7b933',
                'sample-1.out': '3e1ce07401b37846f4d6aab1efbe771b',
                'sample-4.out': '60f3f85857568779dbd10bc4fc506f35',
            })
    def test_call_download_yukicoder_no_260(self):
        self.snippet_call_download(
            'http://yukicoder.me/problems/no/260/', {
                'sample-3.out': '15aac79ea3df9c684a6472d156241987',
                'sample-2.in':  'fdd3527dacad0f949c31f7c4e7fd0c12',
                'sample-2.out': '49a6957c6e2e1c5ce89cde8898949ae1',
                'sample-3.in':  '0ffaa5e4f1ec8fe18e25698504d659ae',
                'sample-1.in':  'b16aaad0c06f931e38ad651115b73f56',
                'sample-1.out': '90e2a51705594d033a3abe9d77b2b7ad',
            })
    def test_call_download_yukicoder_no_8_system(self):
        if 'CI' not in os.environ:
            self.snippet_call_download(
                'https://yukicoder.me/problems/no/8', {
                    '01.txt.in':  '04e90eb0c4a65eefa084dfea8e89de9f',
                    '01.txt.out': 'fc07e56c1012af450b912af02f1e7c30',
                    '02.txt.in':  'e867414a12769d8adc9086093620b4a3',
                    '02.txt.out': '92289ff0469cfacb19a2809e6b44b93a',
                    '03.txt.in':  'c15d6580553f2be2c4b133441da760f3',
                    '03.txt.out': '5ff2d623f9ec55b7207a0e15f076a511',
                    '04.txt.in':  'e28f58da56e572f4f27f9b837a4fe8c5',
                    '04.txt.out': 'b9d27fd37514d704abe776e239029fae',
                    '05.txt.in':  'd04e3cd98784a870b8dae31ab8e2c935',
                    '05.txt.out': '559ffd2e020994c7117fdc38da1dd97d',
                    '06.txt.in':  '897059f9374e64ed03e09a5b5044794c',
                    '06.txt.out': 'a3d50a58dc67267b5e4619ecf73b2dcc',
                    '07.txt.in':  '69d224c83e03e0c3f6ff466fa06bc7dc',
                    '07.txt.out': 'a3d50a58dc67267b5e4619ecf73b2dcc',
                    '08.txt.in':  'de61c37c042526933ac9ff5c99dd8681',
                    '08.txt.out': 'a3d50a58dc67267b5e4619ecf73b2dcc',
                    '09.txt.in':  'b627b556c53cb20b9ae8fa4665925aa9',
                    '09.txt.out': 'a3d50a58dc67267b5e4619ecf73b2dcc',
                    '10.txt.in':  '735f5246a7bde15f85ae368917eee087',
                    '10.txt.out': 'a3d50a58dc67267b5e4619ecf73b2dcc',
                }, is_system=True)
