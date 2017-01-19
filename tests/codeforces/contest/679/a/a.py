#!/usr/bin/env python3
import sys
def query(n):
    print(n)
    sys.stdout.flush()
    return input() == 'yes'
primes = [ 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97 ]
divisors = []
i = 0
k = 1
for _ in range(18):
    n = pow(primes[i], k)
    if n <= 100 and query(n):
        divisors.append(n)
        k += 1
    else:
        k = 1
        i += 1
print('prime' if len(divisors) <= 1 else 'composite')
