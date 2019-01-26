import os
import subprocess
import sys
import unittest

import tests.utils


class GenerateOutputTest(unittest.TestCase):
    def snippet_call_generate_output(self,
                                     args,
                                     input_files,
                                     expected_values,
                                     disallowed_files=None):
        ojtools = os.path.abspath('oj')
        with tests.utils.sandbox(input_files) as tempdir:
            _ = subprocess.check_output(
                [ojtools, 'generate-output'] + args, stderr=sys.stderr)
            for expect in expected_values:
                with open(expect['path']) as f:
                    self.assertEqual(''.join(f.readlines()), expect['data'])
            if disallowed_files is not None:
                for file in disallowed_files:
                    self.assertFalse(os.path.exists(file))

    def test_call_generate_output_simple(self):
        self.snippet_call_generate_output(
            args=['-c', 'cat'],
            input_files=[
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo\n'
                },
                {
                    'path': 'test/sample-2.in',
                    'data': 'bar\n'
                },
            ],
            expected_values=[
                {
                    'path': 'test/sample-1.out',
                    'data': 'foo\n'
                },
                {
                    'path': 'test/sample-2.out',
                    'data': 'bar\n'
                },
            ],
        )

    def test_call_generate_output_select(self):
        self.snippet_call_generate_output(
            args=['-c', 'cat', 'test/sample-1.in', 'test/sample-2.in'],
            input_files=[
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo\n'
                },
                {
                    'path': 'test/sample-2.in',
                    'data': 'bar\n'
                },
                {
                    'path': 'test/sample-3.in',
                    'data': 'baz\n'
                },
            ],
            expected_values=[
                {
                    'path': 'test/sample-1.out',
                    'data': 'foo\n'
                },
                {
                    'path': 'test/sample-2.out',
                    'data': 'bar\n'
                },
            ],
            disallowed_files=['test/sample-3.out'])

    def test_call_generate_output_already_exists(self):
        # Since sample-1.out already exists, sample-1.out will not be updated.
        self.snippet_call_generate_output(
            args=['-c', 'cat'],
            input_files=[
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo\n'
                },
                {
                    'path': 'test/sample-1.out',
                    'data': 'bar\n'
                },
            ],
            expected_values=[
                {
                    'path': 'test/sample-1.out',
                    'data': 'bar\n'
                },
            ],
        )

    def test_call_generate_output_dir(self):
        self.snippet_call_generate_output(
            args=['-c', 'cat', '-d', 'p/o/../../p/o/y/o'],
            input_files=[
                {
                    'path': 'p/o/y/o/sample-1.in',
                    'data': 'foo\n'
                },
                {
                    'path': 'p/o/y/o/sample-2.in',
                    'data': 'bar\n'
                },
            ],
            expected_values=[
                {
                    'path': 'p/o/y/o/sample-1.out',
                    'data': 'foo\n'
                },
                {
                    'path': 'p/o/y/o/sample-2.out',
                    'data': 'bar\n'
                },
            ],
        )

    def test_call_generate_output_format(self):
        self.snippet_call_generate_output(
            args=['-c', 'cat', '-d', 'yuki/coder', '-f', 'test_%e/%s'],
            input_files=[
                {
                    'path': 'yuki/coder/test_in/sample-1.txt',
                    'data': 'foo\n'
                },
                {
                    'path': 'yuki/coder/test_in/sample-2.txt',
                    'data': 'bar\n'
                },
            ],
            expected_values=[
                {
                    'path': 'yuki/coder/test_out/sample-1.txt',
                    'data': 'foo\n'
                },
                {
                    'path': 'yuki/coder/test_out/sample-2.txt',
                    'data': 'bar\n'
                },
            ],
        )

    def test_call_generate_output_format_select(self):
        self.snippet_call_generate_output(
            args=[
                '-c', 'cat', '-d', 'yuki/coder', '-f', 'test_%e/%s',
                'yuki/coder/test_in/sample-2.txt',
                'yuki/coder/test_in/sample-3.txt'
            ],
            input_files=[
                {
                    'path': 'yuki/coder/test_in/sample-2.txt',
                    'data': 'bar\n'
                },
                {
                    'path': 'yuki/coder/test_in/sample-3.txt',
                    'data': 'baz\n'
                },
            ],
            expected_values=[
                {
                    'path': 'yuki/coder/test_out/sample-2.txt',
                    'data': 'bar\n'
                },
                {
                    'path': 'yuki/coder/test_out/sample-3.txt',
                    'data': 'baz\n'
                },
            ],
        )

    def test_call_generate_output_format_hack(self):
        self.snippet_call_generate_output(
            args=['-c', 'cat', '-d', 'a/b', '-f', 'c/test_%e/d/%s/e.case.txt'],
            input_files=[
                {
                    'path': 'a/b/c/test_in/d/sample.case.1/e.case.txt',
                    'data': 'foo\n'
                },
                {
                    'path': 'a/b/c/test_in/d/sample.case.2/e.case.txt',
                    'data': 'bar\n'
                },
            ],
            expected_values=[
                {
                    'path': 'a/b/c/test_out/d/sample.case.1/e.case.txt',
                    'data': 'foo\n'
                },
                {
                    'path': 'a/b/c/test_out/d/sample.case.2/e.case.txt',
                    'data': 'bar\n'
                },
            ],
        )
