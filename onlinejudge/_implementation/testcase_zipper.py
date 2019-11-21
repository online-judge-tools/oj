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
        self._testcases = []  # List[TestCase]
        self._dangling = None  # Optional[Tuple(str, bytes)]

    def add(self, content: bytes, name: str) -> None:
        if self._dangling is None:
            if re.search('output', name, re.IGNORECASE) or re.search('出力', name):
                log.error('strange name for input string: %s', name)
                raise SampleParseError()
            self._dangling = (name, content)
        else:
            if re.search('input', name, re.IGNORECASE) or re.search('入力', name):
                if not (re.search('output', name, re.IGNORECASE) or re.search('出力', name)):  # to ignore titles like "Output for Sample Input 1"
                    log.error('strange name for output string: %s', name)
                    raise SampleParseError()
            index = len(self._testcases)
            input_name, input_content = self._dangling
            self._testcases += [TestCase('sample-{}'.format(index + 1), input_name, input_content, name, content)]
            self._dangling = None

    def get(self) -> List[TestCase]:
        if self._dangling is not None:
            log.error('dangling sample string: %s', self._dangling[1])
            raise SampleParseError
        return self._testcases


def extract_from_files(files: Iterator[Tuple[str, bytes]], format: str = '%s.%e', out: str = 'out') -> List[TestCase]:
    """
    :param out: is the extension for output files. This is used when the zip-file contains files like `sample-1.ans` instead of `sample-1.out`.
    """

    table = {
        's': r'[^/]+',
        'e': r'(in|{})'.format(out),
    }
    names = collections.defaultdict(dict)  # type: Dict[str, Dict[str, Tuple[str, bytes]]]
    for filename, content in files:
        m = onlinejudge._implementation.format_utils.percentparse(filename, format, table)
        assert m
        assert m['e'] not in names[m['s']]
        names[m['s']][m['e']] = (filename, content)
    testcases = []  # type: List[TestCase]
    for name in sorted(names.keys()):
        data = names[name]
        if 'in' not in data or out not in data:
            log.error('dangling sample found: %s', str(data))
            assert False
        else:
            testcases += [TestCase(name, *data['in'], *data[out])]
    return testcases


def extract_from_zip(zip_data: bytes, format: str, out: str = 'out') -> List[TestCase]:
    def iterate():
        with zipfile.ZipFile(io.BytesIO(zip_data)) as fh:
            for filename in fh.namelist():
                if filename.endswith('/'):  # TODO: use `fh.getinfo(filename).is_dir()` after we stop supporting Python 3.5
                    continue
                yield filename, fh.read(filename)

    return extract_from_files(iterate(), format=format, out=out)
