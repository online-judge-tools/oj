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
        cmd = [ self.ojtools, '-v', 'generate-scanner', url ] + options
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
            expected=''.join([
                'int N; cin >> N;\n',
                'vector<int> W(N); for (int i = 0; i < N; ++ i) cin >> W[i];\n',
                ]),
            )
        self.call_generate_scanner(
            url='https://yukicoder.me/problems/no/4',
            expected=''.join([
                'int N; scanf("%d", &N);\n',
                'vector<int> W(N); REP (i, N) scanf("%d", &W[i]);\n',
                ]),
            options=[ '--scanf', '--repeat-macro', 'REP' ]
            )

    def test_call_generate_scanner_yukicoder_vars(self):
        self.call_generate_scanner(
            url='https://yukicoder.me/problems/no/11',
            expected=''.join([
                'int W, H, N; cin >> W >> H >> N;\n',
                'vector<int> S(N), K(N); for (int i = 0; i < N; ++ i) cin >> S[i] >> K[i];\n',
                ]),
            )
        self.call_generate_scanner(
            url='https://yukicoder.me/problems/no/11',
            expected=''.join([
                'int W, H, N; scanf("%d%d%d", &W, &H, &N);\n',
                'vector<int> S(N), K(N); repeat (i, N) scanf("%d%d", &S[i], &K[i]);\n',
                ]),
            options=[ '--scanf', '--repeat-macro', 'repeat' ]
            )

    def test_call_generate_scanner_yukicoder_others(self):
        self.call_generate_scanner(
            url='https://yukicoder.me/problems/no/1',
            expected=''.join([
                'int N, C, V; cin >> N >> C >> V;\n',
                'vector<int> S(V); REP (i, V) cin >> S[i];\n',
                'vector<int> T(V); REP (i, V) cin >> T[i];\n',
                'vector<int> Y(V); REP (i, V) cin >> Y[i];\n',
                'vector<int> M(V); REP (i, V) cin >> M[i];\n',
                ]),
            options=[ '--repeat-macro', 'REP' ],
            )
        self.call_generate_scanner(
            url='https://yukicoder.me/problems/no/12',
            expected=''.join([
                'int N; cin >> N;\n',
                'vector<int> A(N); REP (i, N) cin >> A[i];\n',
                ]),
            options=[ '--repeat-macro', 'REP' ],
            )

    def test_call_generate_scanner_atcoder_others(self):
        self.call_generate_scanner(
            url='https://beta.atcoder.jp/contests/arc083/tasks/arc083_a',
            expected='int A, B, C, D, E, F; cin >> A >> B >> C >> D >> E >> F;\n',
            )
        self.call_generate_scanner(
            url='https://beta.atcoder.jp/contests/abc071/tasks/arc081_a',
            expected=''.join([
                'int N; cin >> N;\n',
                'vector<int> A(N); REP (i, N) cin >> A[i];\n',
                ]),
            options=[ '--repeat-macro', 'REP' ],
            )


if __name__ == '__main__':
    unittest.main()
