import unittest

from onlinejudge_command import main


class RequestExceptionTest(unittest.TestCase):
    def test_invalid_url(self):
        with self.assertRaises(SystemExit) as e:
            main.main(["d", "http://invalid_contest"])
        self.assertEqual(e.exception.code, 1)
