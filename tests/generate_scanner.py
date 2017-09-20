import unittest
import onlinejudge.implementation.logging as log

import subprocess
import os.path
import sys
import time

class GenerateScannerTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cwd = os.getcwd()
        cls.ojtools = os.path.join( cwd, 'oj' )

        # loggin
        log_level = log.logging.INFO
        log.setLevel(log_level)
        handler = log.logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        log.addHandler(handler)

    def call_generate_scanner(self, url, expected, options=[]):
        cmd = [ self.ojtools, 'generate-scanner', url ] + options
        output = subprocess.check_output(cmd, stderr=sys.stderr).decode()
        log.status('result:\n%s', output)
        if expected != output:
            log.error('expected:\n%s' % expected)
        self.assertEqual(expected, output)
        time.sleep(1)

    def test_call_generate_scanner_yukicoder_int(self):
        self.call_generate_scanner(
            url='https://yukicoder.me/problems/no/2',
            expected='int N; cin >> N;\n',
            )
        self.call_generate_scanner(
            url='https://yukicoder.me/problems/no/2',
            expected='int N; scanf("%d", &N);\n',
            options=[ '--scanf' ]
            )

    def test_call_generate_scanner_yukicoder_vector(self):
        self.call_generate_scanner(
            url='https://yukicoder.me/problems/no/4',
            expected='int N; cin >> N;\nvector<int> W(N); for (int i = 0; i < N; ++ i) cin >> W[i];\n',
            )
        self.call_generate_scanner(
            url='https://yukicoder.me/problems/no/4',
            expected='int N; scanf("%d", &N);\nvector<int> W(N); REP (i, N) scanf("%d", &W[i]);\n',
            options=[ '--scanf', '--repeat-macro', 'REP' ]
            )


if __name__ == '__main__':
    unittest.main()
