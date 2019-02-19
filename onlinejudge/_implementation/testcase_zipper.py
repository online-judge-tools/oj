# Python Version: 3.x
# -*- coding: utf-8 -*-
import collections
import io
import re
import zipfile
from typing import *

import onlinejudge._implementation.format_utils
import onlinejudge._implementation.logging as log
from onlinejudge.type import *


class SampleZipper(object):
    def __init__(self):
        self.data = []
        self.dangling = None  # Optional[Tuple(str, str)]

    def add(self, s: str, name: str = '') -> None:
        if self.dangling is None:
            if re.search('output', name, re.IGNORECASE) or re.search('出力', name):
                log.warning('strange name for input string: %s', name)
            self.dangling = (name, s)
        else:
            if re.search('input', name, re.IGNORECASE) or re.search('入力', name):
                if not (re.search('output', name, re.IGNORECASE) or re.search('出力', name)):  # to ignore titles like "Output for Sample Input 1"
                    log.warning('strange name for output string: %s', name)
            index = len(self.data)
            input_name, input_s = self.dangling
            self.data += [TestCase('sample-{}'.format(index + 1), input_name, input_s.encode(), name, s.encode())]
            self.dangling = None

    def get(self) -> List[TestCase]:
        if self.dangling is not None:
            log.error('dangling sample string: %s', self.dangling[1])
        return self.data


def extract_from_zip(zip_data: bytes, format: str, out: str = 'out') -> List[TestCase]:
    table = {
        's': r'[^/]+',
        'e': r'(in|{})'.format(out),
    }
    names = collections.defaultdict(dict)  # type: Dict[str, Dict[str, Tuple[str, bytes]]]
    with zipfile.ZipFile(io.BytesIO(zip_data)) as fh:
        for filename in fh.namelist():
            print(filename)
            if filename.endswith('/'):
                continue
            m = onlinejudge._implementation.format_utils.percentparse(filename, format, table)
            assert m
            assert m['e'] not in names[m['s']]
            names[m['s']][m['e']] = (filename, fh.read(filename))
    samples = []  # type: List[TestCase]
    for name in sorted(names.keys()):
        data = names[name]
        if 'in' not in data or out not in data:
            log.error('dangling sample found: %s', str(data))
            assert False
        else:
            samples += [TestCase(name, *data['in'], *data[out])]
    return samples
