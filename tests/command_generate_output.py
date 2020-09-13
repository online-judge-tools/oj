import os
import unittest

import tests.utils
from tests.utils import cat


class GenerateOutputTest(unittest.TestCase):
    def snippet_call_generate_output(self, args, input_files, expected_values, disallowed_files=None):
        with tests.utils.sandbox(input_files) as _:
            tests.utils.run(['generate-output'] + args, check=True)
            for expect in expected_values:
                with open(expect['path']) as f:
                    self.assertEqual(''.join(f.readlines()), expect['data'])
            if disallowed_files is not None:
                for file in disallowed_files:
                    self.assertFalse(os.path.exists(file))

    def test_call_generate_output_simple(self):
        self.snippet_call_generate_output(
            args=['-c', cat()],
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
        self.snippet_call_generate_output(args=['-c', cat(), 'test/sample-1.in', 'test/sample-2.in'], input_files=[
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
        ], expected_values=[
            {
                'path': 'test/sample-1.out',
                'data': 'foo\n'
            },
            {
                'path': 'test/sample-2.out',
                'data': 'bar\n'
            },
        ], disallowed_files=['test/sample-3.out'])

    def test_call_generate_output_already_exists(self):
        # Since sample-1.out already exists, sample-1.out will not be updated.
        self.snippet_call_generate_output(
            args=['-c', cat()],
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
            args=['-c', cat(), '-d', 'p/o/../../p/o/y/o'],
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
            args=['-c', cat(), '-d', 'yuki/coder', '-f', 'test_%e/%s'],
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
            args=['-c', cat(), '-d', 'yuki/coder', '-f', 'test_%e/%s', 'yuki/coder/test_in/sample-2.txt', 'yuki/coder/test_in/sample-3.txt'],
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
            args=['-c', cat(), '-d', 'a/b', '-f', 'c/test_%e/d/%s/e.case.txt'],
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

    def test_call_generate_output_in_parallel(self):
        TOTAL = 100
        PARALLEL = 32
        input_files = []
        expected_values = []
        for i in range(TOTAL):
            name = 'sample-%03d' % i
            input_files += [{
                'path': 'test/{}.in'.format(name),
                'data': str(i),
            }]
            if i > TOTAL * 0.95:
                input_files += [{
                    'path': 'test/{}.out'.format(name),
                    'data': str(i),
                }]
            expected_values += [{
                'path': 'test/{}.in'.format(name),
                'data': str(i),
            }]
            expected_values += [{
                'path': 'test/{}.out'.format(name),
                'data': str(i),
            }]
        self.snippet_call_generate_output(
            args=['--jobs', str(PARALLEL), '-c', tests.utils.python_c("import sys, time; time.sleep(1); sys.stdout.write(sys.stdin.read())")],
            input_files=input_files,
            expected_values=expected_values,
        )
