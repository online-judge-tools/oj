import unittest
from typing import *

import tests.utils

# The judge program for https://codeforces.com/gym/101021/problem/0
judge_code = """
#!/usr/bin/env python3
import sys
import random
n = random.randint(1, 10 ** 6)
print('[*] n =', n, file=sys.stderr)
for i in range(25 + 1):
    s = input()
    if s.startswith('!'):
        x = int(s.split()[1])
        assert x == n
        exit()
    else:
        print('<' if n < int(s) else '>=')
        sys.stdout.flush()
assert False
"""

accepted_code = """\
#!/usr/bin/env python3
import sys
l = 1
r = 10 ** 6 + 1
while r - l >= 2:
    m = (l + r) // 2
    print(m)
    sys.stdout.flush()
    if input() == '<':
        r = m
    else:
        l = m
print('!', l)
"""

wrong_answer_code = """\
#!/usr/bin/env python3
import sys
x = 21
print(x)
sys.stdout.flush()
if input() == '>=':
    x -= 1
print('!', x)
"""


class TestReactiveTest(unittest.TestCase):
    def test_simple_success(self) -> None:
        files = [
            {
                'path': 'main.py',
                'data': accepted_code,
            },
            {
                'path': 'judge.py',
                'data': judge_code,
            },
        ]
        with tests.utils.sandbox(files):
            tests.utils.run(['t/r', '-c', tests.utils.python_script('main.py'), tests.utils.python_script('judge.py')], check=True)

    def test_simple_failure(self) -> None:
        files = [
            {
                'path': 'main.py',
                'data': wrong_answer_code,
            },
            {
                'path': 'judge.py',
                'data': judge_code,
            },
        ]
        with tests.utils.sandbox(files):
            proc = tests.utils.run(['t/r', '-c', tests.utils.python_script('main.py'), tests.utils.python_script('judge.py')])
            self.assertNotEqual(proc.returncode, 0)
