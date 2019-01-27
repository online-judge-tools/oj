import unittest

import tests.utils

import onlinejudge


class PrintVersionTest(unittest.TestCase):
    def version_test(self):
        result = tests.utils.run_in_sandbox(args=['--version'])
        self.assertTrue(result['proc'].stdout == 'online-judge-tools {}'.format(onlinejudge.__version__))

        result = tests.utils.run_in_sandbox(args=['-version, test'])
        self.assertTrue(result['proc'].stdout == 'online-judge-tools {}'.format(onlinejudge.__version__))
