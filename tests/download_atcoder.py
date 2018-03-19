import unittest
import tests.download

class DownloadAtCoderTest(unittest.TestCase):

    def snippet_call_download(self, *args, **kwargs):
        tests.download.snippet_call_download(self, *args, **kwargs)

    def test_call_download_atcoder_abc001_1(self):
        self.snippet_call_download(
            'http://abc001.contest.atcoder.jp/tasks/abc001_1', {
                'sample-3.out': '0735cf297f0e794bcfa7515f25d189fc',
                'sample-2.in':  'c4da2b805df8425bccc182ad4db8422a',
                'sample-2.out': '897316929176464ebc9ad085f31e7284',
                'sample-3.in':  'e49623ffecc4347eaa5b3e235d5752bd',
                'sample-1.in':  'ec7562c808cc6c106a4d62d212daefd9',
                'sample-1.out': '1dcca23355272056f04fe8bf20edfce0',
            })
    def test_call_download_atcoder_icpc2013spring_a(self):
        self.snippet_call_download(
            'http://jag2013spring.contest.atcoder.jp/tasks/icpc2013spring_a', {
                'sample-3.out': 'e14b420b7266f69a2b2b457f3bbec804',
                'sample-5.out': '3ae2ea0c3867b219ef54d914437e76be',
                'sample-2.in':  '9121f567aad63b98115e8c793a0e2e72',
                'sample-2.out': '3ae2ea0c3867b219ef54d914437e76be',
                'sample-3.in':  'd797a450bb87f8000cda4b45991fc894',
                'sample-1.in':  'b0fba7805dabe2ee3cf299d97a2f6ec2',
                'sample-4.in':  '0ef2e8b0c0a59602c1b4390b58948498',
                'sample-1.out': '3ae2ea0c3867b219ef54d914437e76be',
                'sample-5.in':  '9c8befefed86e886539c9baa85e6724a',
                'sample-4.out': 'e14b420b7266f69a2b2b457f3bbec804',
            })
    def test_call_download_atcoder_arc035_a(self):
        self.snippet_call_download(
            'http://arc035.contest.atcoder.jp/tasks/arc035_a', {
                'sample-3.out': '21da93069c74dfbc3c02999e8f27a712',
                'sample-2.in':  '0bee89b07a248e27c83fc3d5951213c1',
                'sample-2.out': '19541a2746e08a6b8f5145bdbaa23e45',
                'sample-3.in':  '2f597205eff28f4f3561934953478a3c',
                'sample-1.in':  '8911d4ca8a5462050cd9cad1984a86e7',
                'sample-4.in':  '2bb6aed5111ef9726bcf6eef982ff32b',
                'sample-1.out': '21da93069c74dfbc3c02999e8f27a712',
                'sample-4.out': '21da93069c74dfbc3c02999e8f27a712',
            })
    def test_call_download_atcoder_arc001_1(self):
        self.snippet_call_download(
            'http://arc001.contest.atcoder.jp/tasks/arc001_1', {
                'sample-3.out': 'b7ca7cc0db40e50e6575025472fcbeab',
                'sample-2.in':  '178aa146bf65370f626f5b0dc63d6d32',
                'sample-2.out': 'cee9c772621fa0919c3f411e591ae81b',
                'sample-3.in':  '57b9c678fa47979fa44d69bbe60ffadb',
                'sample-1.in':  'ffa1fbc1d14328005da451b67c65d35a',
                'sample-1.out': '3e49d46d6c574dc91c9736436eb06d0a',
            })
    def test_call_download_atcoder_agc001_a(self):
        self.snippet_call_download(
            'http://agc001.contest.atcoder.jp//////tasks//////agc001_a//////?hoge=fuga#piyo', {
                'sample-1.in':  '1aba94ea0ab5e89d4a11b3724bdeb5cc',
                'sample-2.out': '615010a656a5bb29d1898f163619611f',
                'sample-2.in':  'd38a35564e44aa124f04f5088e7203d9',
                'sample-1.out': '6d7fce9fee471194aa8b5b6e47267f03',
            })
    def test_call_download_atcoder_abc073_a(self):
        self.snippet_call_download(
            'https://beta.atcoder.jp/contests/abc073/tasks/abc073_a', {
                'sample-1.in':  '22cab69bca05d296a2d779a52cdee643',
                'sample-1.out': '3ae2ea0c3867b219ef54d914437e76be',
                'sample-2.in':  '8faff61bc1198cc6bdc19adafc27fc82',
                'sample-2.out': 'e14b420b7266f69a2b2b457f3bbec804',
                'sample-3.in':  '80ad60f95c32a3f6e413b5bb7c094e99',
                'sample-3.out': '3ae2ea0c3867b219ef54d914437e76be',
            })
    def test_call_download_atcoder_ddcc2017_qual_a(self):
        self.snippet_call_download(
            'https://beta.atcoder.jp/contests/ddcc2017-qual/tasks/ddcc2017_qual_a', {
                'sample-1.in':  '79b0c0aac7451776e794095b2c596422',
                'sample-1.out': '3ae2ea0c3867b219ef54d914437e76be',
                'sample-2.in':  'ae5b468c7707a1f3d36c49b1fe2ef850',
                'sample-2.out': 'e14b420b7266f69a2b2b457f3bbec804',
                'sample-3.in':  'ed5d34c74e59d16bd6d5b3683db655c3',
                'sample-3.out': 'e14b420b7266f69a2b2b457f3bbec804',
            })
