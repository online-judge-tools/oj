import os
import unittest

import onlinejudge_command.__about__ as version
import tests.utils


class PrintVersionTest(unittest.TestCase):
    def test_version(self):
        result = tests.utils.run_in_sandbox(args=['--version'], files=[])
        self.assertEqual(result['proc'].stdout, 'online-judge-tools {}\n'.format(version.__version__).replace('\n', os.linesep).encode())

        result = tests.utils.run_in_sandbox(args=['--version', 'test'], files=[])
        self.assertEqual(result['proc'].stdout, 'online-judge-tools {}\n'.format(version.__version__).replace('\n', os.linesep).encode())
