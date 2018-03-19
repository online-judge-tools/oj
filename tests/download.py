import unittest

import hashlib
import os
import os.path
import shutil
import subprocess
import sys
import tempfile

def snippet_call_download(self, url, files, is_system=False):
    cwd = os.getcwd()
    ojtools = os.path.join( cwd, 'oj' )
    try:
        tempdir = tempfile.mkdtemp()
        os.chdir(tempdir)
        if os.path.exists('test'):
            shutil.rmtree('test')
        cmd = [ ojtools, 'download', url ]
        if is_system:
            cmd += [ '--system' ]
        subprocess.check_call(cmd, stdout=sys.stdout, stderr=sys.stderr)
        result = {}
        for name in os.listdir('test'):
            with open(os.path.join('test', name)) as fh:
                result[name] = hashlib.md5(fh.buffer.read()).hexdigest()
        self.assertEqual(files, result)
    finally:
        os.chdir(cwd)
        shutil.rmtree(tempdir)

class DownloadOthersTest(unittest.TestCase):

    def snippet_call_download(self, *args, **kwargs):
        snippet_call_download(self, *args, **kwargs)

    def test_call_download_hackerrank_beautiful_array(self):
        if 'CI' not in os.environ:
            self.snippet_call_download(
                'https://www.hackerrank.com/contests/hourrank-1/challenges/beautiful-array', {
                    'sample-1.in':  'fb3f7e56dac548ce73f9d8e485e5336b',
                    'sample-2.out': '897316929176464ebc9ad085f31e7284',
                    'sample-2.in':  '6047a07c8defde4d696513d26e871b20',
                    'sample-1.out': '6d7fce9fee471194aa8b5b6e47267f03',
                })

    def test_call_download_anarchygolf_the_b_programming_language(self):
        self.snippet_call_download(
            'http://golf.shinh.org/p.rb?The+B+Programming+Language', {
                'sample-3.out': 'fcbee46b3b888607abe720d598c75b17',
                'sample-2.in':  '810d1189284ef048fc30f80ba7a22c6d',
                'sample-2.out': 'd4e62449830b2a986024d914b194f129',
                'sample-3.in':  '7361217616875a437a3d6b41612dacbb',
                'sample-1.in':  '3de90f793f16fad76da1527e09b8e528',
                'sample-1.out': 'f67b46b3c53308d8a6414b20092a2220',
            })
    def test_call_download_anarchygolf_simple_language(self):
        self.snippet_call_download(
            'http://golf.shinh.org/p.rb?simple+language', {
                'sample-3.out': 'c4211571f7a72cfad092b4dac7b15144',
                'sample-2.in':  '10e10b554ef9bc07d56a514d2f6dab26',
                'sample-2.out': '48a24b70a0b376535542b996af517398',
                'sample-3.in':  'f201f3f6606e56f561f8452c9a60210b',
                'sample-1.in':  '9b3c9ece5285bb1bcd1164cec8aa4243',
                'sample-1.out': '48a24b70a0b376535542b996af517398',
            })
    def test_call_download_anarchygolf_hello_world(self):
        self.snippet_call_download(
            'http://golf.shinh.org/p.rb?hello+world', {
                'sample-1.in':  'd41d8cd98f00b204e9800998ecf8427e',
                'sample-1.out': '746308829575e17c3331bbcb00c0898b',
            })
    def test_call_download_anarchygolf_momomo(self):
        self.snippet_call_download(
            'http://golf.shinh.org/p.rb?momomo', {
                'sample-1.in':  '281e30fff54f179881c67c4d0564633e',
                'sample-1.out': 'd67adc236dd84fd82fb4598922d5cf32',
            })

    def test_call_download_codeforces_problemset_700_b(self):
        self.snippet_call_download(
            'http://codeforces.com/problemset/problem/700/B', {
                'sample-1.in':  '1f38b0f27f4b0005e5409e834ff59166',
                'sample-2.out': '7c5aba41f53293b712fd86d08ed5b36e',
                'sample-2.in':  '8a8c08b2901d4cfca41ad0703dfa718e',
                'sample-1.out': '9ae0ea9e3c9c6e1b9b6252c8395efdc1',
            })
    def test_call_download_codeforces_contest_538_h(self):
        self.snippet_call_download(
            'http://codeforces.com/contest/538/problem/H', {
                'sample-1.in':  'c8483ca371b414e911ccbecf239beed6',
                'sample-2.out': '87a45b8adc25c7bf37eaa25b530de79c',
                'sample-2.in':  'afa0c8b2336e798b5f29a200a18432d1',
                'sample-1.out': '166a3645f3c31595526624ce003b41fc',
            })
    def test_call_download_codeforces_gym_101021_a(self):
        self.snippet_call_download(
            'http://codeforces.com/gym/101021/problem/A', {
                'sample-1.in':  '4dfb06c20503a3f0dbe0fb29dd52d304',
                'sample-2.out': '614a0c8025f8bbcf46b8ba0ff9fd61d1',
                'sample-2.in':  'dcfe1f14721a0e141c2e31adeebe7a53',
                'sample-1.out': '45778e8e2d350841cf68711ece5cb9e1',
            })

    def test_call_download_csacademy_k_swap(self):
        self.snippet_call_download(
            'https://csacademy.com/contest/round-39/task/k-swap/', {
                'sample-1.in':  '2ce34946200aa66529dbc96b411e2450',
                'sample-1.out': '78c6d00be497cd50311743df6c8de3ea',
                'sample-2.in':  '65625b1f27b94fc2c5b6532a18f93070',
                'sample-2.out': '16324a714d2c6f4f9feefe65f0784094',
                'sample-3.in':  '8e92bd4fb348c40f78a13c56a1f5a937',
                'sample-3.out': 'c31f209a3d0412a16c4b93e4ee060b54',
            })
    def test_call_download_csacademy_unfair_game(self):
        self.snippet_call_download(
            'https://csacademy.com/contest/archive/task/unfair_game/', {
                'sample-1.in':  '57cce69a08e8dd833a9f9aa3b6d13a40',
                'sample-1.out': '367764329430db34be92fd14a7a770ee',
                'sample-2.in':  '46b87e796b61eb9b8970e83c93a02809',
                'sample-2.out': 'eb844645e8e61de0a4cf4b991e65e63e',
            })
