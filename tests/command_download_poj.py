import os
import unittest

import tests.command_download


class DownloadPOJTest(unittest.TestCase):
    def snippet_call_download(self, *args, **kwargs):
        tests.command_download.snippet_call_download(self, *args, **kwargs)

    def test_call_download_poj_1000(self):
        self.snippet_call_download(
            'http://poj.org/problem?id=1000', [
                {
                    "name": "sample",
                    "input": "1 2\r\n",
                    "output": "3\r\n"
                },
            ], type='json')

    def test_call_download_poj_2104(self):
        self.snippet_call_download(
            'http://poj.org/problem?id=2104', [
                {
                    "name": "sample",
                    "input": "7 3\r\n1 5 2 6 3 7 4\r\n2 5 3\r\n4 4 1\r\n1 7 3\r\n",
                    "output": "5\r\n6\r\n3\r\n"
                },
            ], type='json')

    def test_call_download_poj_3150(self):
        self.snippet_call_download(
            'http://poj.org/problem?id=3150', [
                {
                    "input": "5 3 1 1\r\n1 2 2 1 2\r\n",
                    "output": "2 2 2 2 1\r\n"
                },
                {
                    "input": "5 3 1 10\r\n1 2 2 1 2\r\n",
                    "output": "2 0 0 2 2\r\n"
                },
            ], type='json')
