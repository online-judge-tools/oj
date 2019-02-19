import os
import unittest

import tests.command_download


class DownloadCSAcademyTest(unittest.TestCase):
    def snippet_call_download(self, *args, **kwargs):
        tests.command_download.snippet_call_download(self, *args, **kwargs)

    def test_call_download_csacademy_k_swap(self):
        self.snippet_call_download('https://csacademy.com/contest/round-39/task/k-swap/', {
            'sample-0.in': '2ce34946200aa66529dbc96b411e2450',
            'sample-0.out': '78c6d00be497cd50311743df6c8de3ea',
            'sample-1.in': '65625b1f27b94fc2c5b6532a18f93070',
            'sample-1.out': '16324a714d2c6f4f9feefe65f0784094',
            'sample-2.in': '8e92bd4fb348c40f78a13c56a1f5a937',
            'sample-2.out': 'c31f209a3d0412a16c4b93e4ee060b54',
        })

    def test_call_download_csacademy_unfair_game(self):
        self.snippet_call_download('https://csacademy.com/contest/archive/task/unfair_game/', {
            'sample-0.in': '57cce69a08e8dd833a9f9aa3b6d13a40',
            'sample-0.out': '367764329430db34be92fd14a7a770ee',
            'sample-1.in': '46b87e796b61eb9b8970e83c93a02809',
            'sample-1.out': 'eb844645e8e61de0a4cf4b991e65e63e',
        })
