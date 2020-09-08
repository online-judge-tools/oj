import unittest

import tests.command_download


# TODO: move these tests to https://github.com/online-judge-tools/api-client
class DownloadAnarchyGolfTest(unittest.TestCase):
    def snippet_call_download(self, *args, **kwargs):
        tests.command_download.snippet_call_download(self, *args, **kwargs)

    def test_call_download_anarchygolf_the_b_programming_language(self):
        self.snippet_call_download('http://golf.shinh.org/p.rb?The+B+Programming+Language', {
            'sample-1.in': '3de90f793f16fad76da1527e09b8e528',
            'sample-1.out': 'f67b46b3c53308d8a6414b20092a2220',
            'sample-2.in': '810d1189284ef048fc30f80ba7a22c6d',
            'sample-2.out': 'd4e62449830b2a986024d914b194f129',
            'sample-3.in': '7361217616875a437a3d6b41612dacbb',
            'sample-3.out': 'fcbee46b3b888607abe720d598c75b17',
        })

    def test_call_download_anarchygolf_simple_language(self):
        self.snippet_call_download('http://golf.shinh.org/p.rb?simple+language', {
            'sample-1.in': 'fa50b8b616463173474302ca3e63586b',
            'sample-1.out': 'a87ff679a2f3e71d9181a67b7542122c',
            'sample-2.in': '99f5fea6d83f6e55f7d7bca6f7fd1fa3',
            'sample-2.out': 'a87ff679a2f3e71d9181a67b7542122c',
            'sample-3.in': '2959791426cb059fce835d1062b655b3',
            'sample-3.out': '0e04717a220a3bd93e92aceb18d71638',
        })

    def test_call_download_anarchygolf_hello_world(self):
        self.snippet_call_download('http://golf.shinh.org/p.rb?hello+world', {
            'sample-1.in': 'd41d8cd98f00b204e9800998ecf8427e',
            'sample-1.out': '746308829575e17c3331bbcb00c0898b',
        })

    def test_call_download_anarchygolf_momomo(self):
        self.snippet_call_download('http://golf.shinh.org/p.rb?momomo', {
            'sample-1.in': '281e30fff54f179881c67c4d0564633e',
            'sample-1.out': 'd67adc236dd84fd82fb4598922d5cf32',
        })
