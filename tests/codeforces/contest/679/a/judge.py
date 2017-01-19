#!/usr/bin/env python3
import sys
# import argparse
# parser = argparse.ArgumentParser()
# parser.add_argument('input')
# args = parser.parse_args()
# with open(args.input) as fh:
#     n = int(fh.read())
import random
n = random.randint(2, 100)
assert 2 <= n <= 100
is_prime = all(n % i != 0 for i in range(2, n-1))
for _ in range(20):
    line = input().strip()
    if line == 'prime':
        result = ['WA', 'AC'][is_prime]
        break
    elif line == 'composite':
        result = ['WA', 'AC'][not is_prime]
        break
    else:
        k = int(line)
        print(['no', 'yes'][n % k == 0])
        sys.stdin.flush()
else:
    result = 'QLE'
assert result == 'AC'
