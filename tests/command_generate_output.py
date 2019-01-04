import unittest

import contextlib
import filecmp
import glob
import os
import subprocess
import sys


@contextlib.contextmanager
def chdir(path):
    cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        for file in glob.glob('*/*.out'):
            os.remove(file)
        os.chdir(cwd)

class TestGenerateOutput(unittest.TestCase):

    def snippet_call_test(self, args, input_files, output_files):
        ojtools = os.path.abspath('oj')
        with chdir('tests/generate_output_testcases/'):
            _ = subprocess.check_output([ojtools, '-v', 'generate-output'] + args, stderr=sys.stderr)
            for input_file, output_file in zip(input_files, output_files):
                self.assertTrue(filecmp.cmp(input_file, output_file, shallow=False))

    def test_call_generate_output_simple(self):
        self.snippet_call_test(
            args=[ '-c', 'cat' ],
            input_files=[ 'test/sample-1.in',
                    'test/sample-2.in' ],
            output_files=[ 'test/sample-1.out',
                          'test/sample-2.out' ],
        )

    def test_call_test_select(self):
        self.snippet_call_test(
            args=[ '-c', 'cat', 'test/sample-1.in', 'test/sample-2.in' ],
            input_files=['test/sample-1.in',
                         'test/sample-2.in'],
            output_files = ['test/sample-1.out',
                            'test/sample-2.out'],
        )

unittest.main()