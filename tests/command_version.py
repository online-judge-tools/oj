import unittest

import tests.utils


class PrintVersionTest(unittest.TestCase):
    def test_version(self):
        pattern = rb'^online-judge-tools \d+\.\d+\.\d+ \(\+ online-judge-api-client \d+\.\d+\.\d+\)$'
        result = tests.utils.run_in_sandbox(args=['--version'], files=[])
        self.assertRegex(result['proc'].stdout.strip(), pattern)
