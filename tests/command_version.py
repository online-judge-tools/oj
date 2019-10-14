import os
import unittest

import tests.utils

import onlinejudge


class PrintVersionTest(unittest.TestCase):
    def test_version(self):
        result = tests.utils.run_in_sandbox(args=['--version'], files=[])
        self.assertEqual(result['proc'].stdout, 'online-judge-tools {}\n'.format(onlinejudge.__version__).replace('\n', os.linesep).encode())

        result = tests.utils.run_in_sandbox(args=['--version', 'test'], files=[])
        self.assertEqual(result['proc'].stdout, 'online-judge-tools {}\n'.format(onlinejudge.__version__).replace('\n', os.linesep).encode())
