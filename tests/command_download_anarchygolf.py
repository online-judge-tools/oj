import os
import unittest

import tests.command_download


class DownloadAnarchyGolfTest(unittest.TestCase):
    def snippet_call_download(self, *args, **kwargs):
        tests.command_download.snippet_call_download(self, *args, **kwargs)

    def test_call_download_anarchygolf_the_b_programming_language(self):
        self.snippet_call_download('http://golf.shinh.org/p.rb?The+B+Programming+Language', {
            'sample-3.out': 'fcbee46b3b888607abe720d598c75b17',
            'sample-2.in': '810d1189284ef048fc30f80ba7a22c6d',
            'sample-2.out': 'd4e62449830b2a986024d914b194f129',
            'sample-3.in': '7361217616875a437a3d6b41612dacbb',
            'sample-1.in': '3de90f793f16fad76da1527e09b8e528',
            'sample-1.out': 'f67b46b3c53308d8a6414b20092a2220',
        })

    def test_call_download_anarchygolf_simple_language(self):
        self.snippet_call_download('http://golf.shinh.org/p.rb?simple+language', {
            'sample-3.out': 'c4211571f7a72cfad092b4dac7b15144',
            'sample-2.in': '10e10b554ef9bc07d56a514d2f6dab26',
            'sample-2.out': '48a24b70a0b376535542b996af517398',
            'sample-3.in': 'f201f3f6606e56f561f8452c9a60210b',
            'sample-1.in': '9b3c9ece5285bb1bcd1164cec8aa4243',
            'sample-1.out': '48a24b70a0b376535542b996af517398',
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
