import unittest

import tests.command_download


class DownloadLibraryCheckerTest(unittest.TestCase):
    def snippet_call_download(self, *args, **kwargs):
        tests.command_download.snippet_call_download(self, *args, **kwargs)

    def test_call_download_library_checker_aplusb_system(self):
        self.snippet_call_download('https://judge.yosupo.jp/problem/aplusb', [
            {
                "name": "example_00",
                "input": "1234 5678\n",
                "output": "6912\n"
            },
            {
                "name": "example_01",
                "input": "1000000000 1000000000\n",
                "output": "2000000000\n"
            },
            {
                "name": "random_00",
                "input": "192279220 156648746\n",
                "output": "348927966\n"
            },
            {
                "name": "random_01",
                "input": "264704197 120999146\n",
                "output": "385703343\n"
            },
            {
                "name": "random_02",
                "input": "682152023 451794314\n",
                "output": "1133946337\n"
            },
            {
                "name": "random_03",
                "input": "627477696 504915182\n",
                "output": "1132392878\n"
            },
            {
                "name": "random_04",
                "input": "729561619 415335212\n",
                "output": "1144896831\n"
            },
            {
                "name": "random_05",
                "input": "173330281 220603612\n",
                "output": "393933893\n"
            },
            {
                "name": "random_06",
                "input": "841413509 58432763\n",
                "output": "899846272\n"
            },
            {
                "name": "random_07",
                "input": "251229786 256388306\n",
                "output": "507618092\n"
            },
            {
                "name": "random_08",
                "input": "118232767 222490630\n",
                "output": "340723397\n"
            },
            {
                "name": "random_09",
                "input": "907649120 290651129\n",
                "output": "1198300249\n"
            },
        ], type='json', is_system=True)

    def test_call_download_library_checker_unionfind(self):
        self.snippet_call_download('https://judge.yosupo.jp/problem/unionfind', [
            {
                "name": "example_00",
                "input": "4 7\n1 0 1\n0 0 1\n0 2 3\n1 0 1\n1 1 2\n0 0 2\n1 1 3\n",
                "output": "0\n1\n0\n1\n"
            },
        ], type='json')
