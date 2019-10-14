import os
import unittest

import tests.utils

import onlinejudge
from onlinejudge._implementation import utils


class PrintVersionTest(unittest.TestCase):
    def version_test(self):
        result = tests.utils.run_in_sandbox(args=['--version'])
        self.assertTrue(result['proc'].stdout == 'online-judge-tools {}'.format(onlinejudge.__version__))

        result = tests.utils.run_in_sandbox(args=['-version, test'])
        self.assertTrue(result['proc'].stdout == 'online-judge-tools {}'.format(onlinejudge.__version__))

    def get_latest_version_test(self):
        version_cache_path = utils.cache_dir / "pypi.json"

        # without cache
        os.remove(version_cache_path)
        self.assertEqual(utils.get_latest_version_from_pypi(), onlinejudge.__version__)

        # from cache
        self.assertEqual(utils.get_latest_version_from_pypi(), onlinejudge.__version__)
