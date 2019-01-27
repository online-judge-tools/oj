import unittest

import onlinejudge
import tests.utils

class PrintVersionTest(unittest.TestCase):
    def version_test(self):
        result = tests.utils.run_in_sandbox(
            args=['-V'])
        self.assertTrue(result['proc'].stdout == 'online-judge-tools {}'.format(onlinejudge.__version__))

        result = tests.utils.run_in_sandbox(
            args=['--version'])
        self.assertTrue(result['proc'].stdout == 'online-judge-tools {}'.format(onlinejudge.__version__))

        result = tests.utils.run_in_sandbox(
            args=['-V, -test'])
        self.assertTrue(result['proc'].stdout == 'online-judge-tools {}'.format(onlinejudge.__version__))

