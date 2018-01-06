# Python Version: 3.x
import onlinejudge
import onlinejudge.implementation.utils as utils
import onlinejudge.implementation.logging as log
import string
import os
import os.path
import subprocess
import contextlib


def get_char_class(c):
    assert isinstance(c, int)
    assert 0 <= c < 256
    if chr(c) in string.ascii_letters + string.digits:
        return 'alnum'
    elif chr(c) in ' \t\n':
        return 'whitespace'
    elif 32 < c < 127:
        return 'symbol'
    else:
        return 'binary'

def get_statistics(s):
    assert isinstance(s, bytes)
    stat = {
        'binary': 0,
        'alnum': 0,
        'symbol': 0,
        'whitespace': 0,
    }
    for c in s:
        stat[get_char_class(c)] += 1
    return stat

def code_statistics(args):
    with open(args.file, 'rb') as fh:
        code = fh.read()
    stat = get_statistics(code)
    stat['size'] = len(code)
    for key in ( 'size', 'binary', 'alnum', 'symbol', 'whitespace' ):
        log.info('%s = %d', key, stat[key])
