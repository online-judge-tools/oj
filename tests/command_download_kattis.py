import os
import unittest

import tests.command_download


class DownloadKattisTest(unittest.TestCase):
    def snippet_call_download(self, *args, **kwargs):
        tests.command_download.snippet_call_download(self, *args, **kwargs)

    def test_call_download_kattis_8queens(self):
        self.snippet_call_download(
            'https://open.kattis.com/contests/asiasg15prelwarmup/problems/8queens', [
                {
                    "name": "example00",
                    "input": "*.......\n..*.....\n....*...\n......*.\n.*......\n.......*\n.....*..\n...*....\n",
                    "output": "invalid\n"
                },
                {
                    "name": "example01",
                    "input": "*.......\n......*.\n....*...\n.......*\n.*......\n...*....\n.....*..\n..*.....\n",
                    "output": "valid\n"
                },
            ], type='json')

    def test_call_download_kattis_hanoi18_a(self):
        self.snippet_call_download(
            'https://hanoi18.kattis.com/problems/amazingadventures', [
                {
                    "name": "1",
                    "input": "3 3\n1 1\n3 3\n2 1\n2 2\n\n3 4\n1 1\n3 4\n2 1\n1 2\n\n2 2\n2 1\n2 2\n1 2\n1 1\n\n0 0\n",
                    "output": "YES\nRRUULLD\nNO\nYES\nRD\n"
                },
            ], type='json')

    def test_call_download_kattis_hello(self):
        # there is no sample cases (and no samples.zip; it returns 404)
        self.snippet_call_download('https://open.kattis.com/problems/hello', [], type='json')
