import unittest

import requests.exceptions
import tests.command_download


class DownloadInvalid(unittest.TestCase):
    def snippet_call_download_raises(self, *args, **kwargs):
        tests.command_download.snippet_call_download_raises(self, *args, **kwargs)

    def test_call_download_invalid(self):
        self.snippet_call_download_raises(requests.exceptions.InvalidURL, 'https://not_exist_contest.jp/tasks/001_a')
