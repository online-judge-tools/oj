import os
import shutil
import time
import unittest

import requests.exceptions

import tests.utils
from onlinejudge.service.atcoder import AtCoderService
from onlinejudge.service.codeforces import CodeforcesService
from onlinejudge.service.hackerrank import HackerRankService
from onlinejudge.service.toph import TophService
from onlinejudge.service.yukicoder import YukicoderService


class SubmitArgumentsTest(unittest.TestCase):
    @unittest.skipIf(not tests.utils.is_logged_in(AtCoderService()), 'login is required')
    def test_call_submit_atcoder_practice_2_with_history_simple(self):

        url = 'https://atcoder.jp/contests/practice/tasks/practice_2'
        files = [
            {
                'path': 'a.cpp',
                'data': 'compile error'
            },
        ]
        with tests.utils.sandbox(files):
            tests.utils.run(['dl', url], check=False)
            tests.utils.run(['s', '-y', '--no-open', url, 'a.cpp'], check=True)

    @unittest.skipIf(not tests.utils.is_logged_in(AtCoderService()), 'login is required')
    def test_call_submit_atcoder_practice_2_with_history_remove(self):

        url = 'https://atcoder.jp/contests/practice/tasks/practice_2'
        files = [
            {
                'path': 'a.cpp',
                'data': 'compile error'
            },
        ]
        with tests.utils.sandbox(files):
            tests.utils.run(['dl', 'https://atcoder.jp/contests/abc099/tasks/abc099_a'], check=True)
            shutil.rmtree('test/')
            tests.utils.run(['dl', url], check=False)
            tests.utils.run(['s', '-y', '--no-open', url, 'a.cpp'], check=True)

    @unittest.skipIf(os.name == 'nt', "shell script doesn't work on Windows")
    @unittest.skipIf(not tests.utils.is_logged_in(AtCoderService()), 'login is required')
    def test_call_submit_atcoder_practice_1_with_open(self):

        url = 'https://atcoder.jp/contests/practice/tasks/practice_1'
        files = [
            {
                'path': 'a.pl',
                'data': 'print<>+(<>=~$",$`+$\'),$",<>'
            },
            {
                'path': 'browse.sh',
                'data': '#!/bin/sh\necho "$@" > url.txt\n',
                'executable': True,
            },
        ]
        with tests.utils.sandbox(files) as tempdir:
            env = dict(os.environ)
            env['BROWSER'] = os.path.join(tempdir, 'browse.sh')

            tests.utils.run(['s', '-y', '--open', url, 'a.pl'], env=env, check=True)
            with open('url.txt') as fh:
                url = fh.read().strip()
            self.assertTrue(url.startswith('https://atcoder.jp/contests/practice/submissions/'))

    @unittest.skipIf(not tests.utils.is_logged_in(AtCoderService()), 'login is required')
    def test_call_submit_atcoder_invalid_url(self):

        url = 'https://atcoder.jp/contests/practice/tasks/practice_111'
        code = '''\
        #include <bits/stdc++.h>
        using namespace std;
        int main() {
            int a; cin >> a;
            int b, c; cin >> b >> c;
            string s; cin >> s;
            cout << a + b + c << ' ' << s << endl;
            return 0;
        }
        '''
        files = [
            {
                'path': 'main.cpp',
                'data': code
            },
        ]

        with tests.utils.sandbox(files):
            with self.assertRaises(requests.exceptions.HTTPError):
                tests.utils.run(["submit", '-y', '--no-open', url, 'main.cpp'], check=True)


class SubmitAtCoderTest(unittest.TestCase):
    @unittest.skipIf(not tests.utils.is_logged_in(AtCoderService()), 'login is required')
    def test_call_submit_practice_1(self):

        url = 'https://atcoder.jp/contests/practice/tasks/practice_1'
        code = '''\
#include <bits/stdc++.h>
using namespace std;
int main() {
    int a; cin >> a;
    int b, c; cin >> b >> c;
    string s; cin >> s;
    cout << a + b + c << ' ' << s << endl;
    return 0;
}
'''
        files = [
            {
                'path': 'main.cpp',
                'data': code
            },
        ]

        with tests.utils.sandbox(files):
            tests.utils.run(['submit', '-y', '--no-open', url, 'main.cpp'], check=True)

    @unittest.skipIf(not tests.utils.is_logged_in(AtCoderService()), 'login is required')
    def test_call_submit_practice_2(self):

        url = 'https://atcoder.jp/contests/practice/tasks/practice_2'
        code = '''\
# Python Version: 3.x
import string
import sys
def quick_sort(s):
    if len(s) <= 1:
        return s
    pivot = s[0]
    lo, hi = '', ''
    for c in s[1 :]:
        print('?', pivot, c)
        sys.stdout.flush()
        if input() == '<':
            hi += c
        else:
            lo += c
    return quick_sort(lo) + pivot + quick_sort(hi)
n, q = map(int, input().split())
assert n == 26 and q == 1000
print('!', ''.join(quick_sort(string.ascii_uppercase[: n])))
'''
        files = [
            {
                'path': 'main.py',
                'data': code
            },
        ]

        with tests.utils.sandbox(files):
            tests.utils.run(['submit', '-y', '--no-open', url, 'main.py'], check=True)


class SubmitCodeforcesTest(unittest.TestCase):
    @unittest.skipIf(not tests.utils.is_logged_in(CodeforcesService()), 'login is required')
    def test_call_submit_beta_1_a(self):

        url = 'https://codeforces.com/contest/1/problem/A'
        code = '\n'.join([
            '#!/usr/bin/env python3',
            'h, w, a = map(int, input().split())',
            'print(((h + a - 1) // a) * ((w + a - 1) // a))',
            '# ' + str(int(time.time())),  # to bypass the "You have submitted exactly the same code before" error
        ]) + '\n'
        files = [
            {
                'path': 'a.py',
                'data': code
            },
        ]
        with tests.utils.sandbox(files):
            tests.utils.run(['s', '-y', '--no-open', url, 'a.py'], check=True)

    @unittest.skipIf(not tests.utils.is_logged_in(CodeforcesService()), 'login is required')
    def test_call_submit_beta_3_b(self):

        url = 'https://codeforces.com/contest/3/problem/B'
        code = r'''#include <bits/stdc++.h>
#define REP(i, n) for (int i = 0; (i) < (int)(n); ++ (i))
#define ALL(x) begin(x), end(x)
using namespace std;

int main() {
    // input
    int n, v; cin >> n >> v;
    vector<pair<int, int> > one;
    vector<tuple<int, int, int> > two;
    REP (i, n) {
        int t, p; cin >> t >> p;
        if (t == 1) {
            one.emplace_back(p, i);
        } else {
            two.emplace_back(p, i, -1);
        }
    }

    // solve
    int sum_p = 0;
    vector<int> used;
    sort(ALL(one));
    if (v % 2 == 1 and not one.empty()) {
        int p_i, i; tie(p_i, i) = one.back();
        one.pop_back();
        sum_p += p_i;
        used.push_back(i);
        v -= 1;
    }
    while (one.size() >= 2) {
        int p_i, i; tie(p_i, i) = one.back();
        one.pop_back();
        int p_j, j; tie(p_j, j) = one.back();
        one.pop_back();
        two.emplace_back(p_i + p_j, i, j);
    }
    if (one.size() == 1) {
        int p_i, i; tie(p_i, i) = one.back();
        two.emplace_back(p_i, i, -1);
        one.pop_back();
    }
    sort(ALL(two));
    while (v >= 2 and not two.empty()) {
        int p, i, j; tie(p, i, j) = two.back();
        two.pop_back();
        sum_p += p;
        used.push_back(i);
        if (j != -1) used.push_back(j);
        v -= 2;
    }

    // output
    cout << sum_p << endl;
    REP (i, used.size()) {
        cout << used[i] + 1 << (i + 1 < used.size() ? ' ' : '\n');
    }
    return 0;
}
''' + '// ' + str(int(time.time())) + '\n'  # to bypass the "You have submitted exactly the same code before" error
        files = [
            {
                'path': 'main.cpp',
                'data': code
            },
        ]
        with tests.utils.sandbox(files):
            tests.utils.run(['s', '-y', '--no-open', url, 'main.cpp'], check=True)


class SubmitYukicoderTest(unittest.TestCase):
    @unittest.skipIf(not tests.utils.is_logged_in(YukicoderService()), 'login is required')
    def test_call_submit_9000(self):

        url = 'https://yukicoder.me/problems/no/9000'
        code = '\n'.join([
            '#!/usr/bin/env python2',
            'print "Hello World!"',
        ]) + '\n'
        files = [
            {
                'path': 'a.py',
                'data': code
            },
        ]
        with tests.utils.sandbox(files):
            tests.utils.run(['s', '-y', '--no-open', url, 'a.py'], check=True)

    @unittest.skipIf(not tests.utils.is_logged_in(YukicoderService()), 'login is required')
    def test_call_submit_beta_3_b(self):

        url = 'https://yukicoder.me/problems/527'
        code = r'''#include <bits/stdc++.h>
using namespace std;
int main() {
    int a, b; cin >> a >> b;
    string s; cin >> s;
    cout << a + b << ' ' << s << endl;
    return 0;
}
'''
        files = [
            {
                'path': 'main.cpp',
                'data': code
            },
        ]
        with tests.utils.sandbox(files):
            tests.utils.run(['s', '-y', '--no-open', url, 'main.cpp'], check=True)


class SubmitHackerRankTest(unittest.TestCase):
    @unittest.skipIf(not tests.utils.is_logged_in(HackerRankService()), 'login is required')
    def test_call_submit_worldcodesprint_mars_exploration(self):
        url = 'https://www.hackerrank.com/contests/worldcodesprint/challenges/mars-exploration'
        code = '''#!/usr/bin/env python3
s = input()
ans = 0
for i in range(len(s) // 3):
    if s[3 * i] != 'S':
        ans += 1
    if s[3 * i + 1] != 'O':
        ans += 1
    if s[3 * i + 2] != 'S':
        ans += 1
print(ans)
'''
        files = [
            {
                'path': 'a.py',
                'data': code
            },
        ]
        with tests.utils.sandbox(files):
            tests.utils.run(['s', '-y', '--no-open', url, 'a.py'], check=True)


class SubmitTophTest(unittest.TestCase):
    @unittest.skipIf(not tests.utils.is_logged_in(TophService()), 'login is required')
    def test_call_submit_copycat(self):
        url = 'https://toph.co/p/copycat'
        code = '''#!/usr/bin/env python3
s = input()
print(s)
'''
        files = [
            {
                'path': 'a.py',
                'data': code
            },
        ]
        with tests.utils.sandbox(files):
            tests.utils.run(['s', '-l', '58482c1804469e2585024324', '-y', '--no-open', url, 'a.py'], check=True)

    @unittest.skipIf(not tests.utils.is_logged_in(TophService()), 'login is required')
    def test_call_submit_divisors(self):
        url = 'https://toph.co/p/divisors'
        code = '''#include<bits/stdc++.h>
using namespace std;
int main()
{
    int a;
    cin>>a;
    for (int i=1;i<=a;i++)
    {
        if (a%i==0)
        {
            cout <<i<<endl;
        }
    }
}
'''
        files = [
            {
                'path': 'a.cpp',
                'data': code
            },
        ]
        with tests.utils.sandbox(files):
            tests.utils.run(['s', '-y', '--no-open', url, 'a.cpp'], check=True)
