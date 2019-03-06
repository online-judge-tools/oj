import os
import unittest

import tests.command_download


class DownloadTophTest(unittest.TestCase):
    def snippet_call_download(self, *args, **kwargs):
        tests.command_download.snippet_call_download(self, *args, **kwargs)

    def test_call_download_toph_new_year_couple(self):
        self.snippet_call_download('https://toph.co/p/new-year-couple', {
            'sample-2.out': 'a147d4af6796629a62fa43341f0e0bdf',
            'sample-2.in': 'fc1dbb7bb49bfbb37e7afe9a64d2f89b',
            'sample-1.in': 'd823c94a5bbd1af3161ad8eb4e48654e',
            'sample-1.out': '0f051fce168dc5aa9e45605992cd63c5',
        })

    def test_call_download_toph_power_and_mod(self):
        self.snippet_call_download('https://toph.co/p/power-and-mod', {
            'sample-1.in': '46e186317c8c10d9452d6070f6c63b09',
            'sample-1.out': 'ad938662144b559bff344ff266f9d1cc',
        })
