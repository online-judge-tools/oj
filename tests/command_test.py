import json
import os
import pathlib
import random
import shutil
import sys
import unittest

import tests.utils
from testfixtures import LogCapture
from tests.utils import cat, sleep_1sec

from onlinejudge._implementation import logging
from onlinejudge._implementation.command import test


class TestTest(unittest.TestCase):
    def snippet_call_test(self, args, files, expected, verbose=True):
        result = tests.utils.run_in_sandbox(args=(['-v'] if verbose else []) + ['test', '--json'] + args, files=files)
        self.assertTrue(result['proc'].stdout)
        data = json.loads(result['proc'].stdout.decode())
        if expected is None:
            return data
        else:
            self.assertEqual(len(data), len(expected))
            for a, b in zip(data, expected):
                self.assertEqual(a['testcase']['name'], b['testcase']['name'])
                self.assertEqual(a['testcase']['input'], b['testcase']['input'].replace('/', os.path.sep) % result['tempdir'])
                self.assertEqual('output' in a['testcase'], 'output' in b['testcase'])
                if 'output' in b['testcase']:
                    self.assertEqual(a['testcase']['output'], b['testcase']['output'].replace('/', os.path.sep) % result['tempdir'])
                self.assertEqual(a['exitcode'], b['exitcode'])
                self.assertEqual(a['status'], b['status'])
                self.assertEqual(a['output'].replace(os.linesep, '\n'), b['output'])

    def test_call_test_simple(self):
        self.snippet_call_test(
            args=['-c', cat()],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo\n'
                },
                {
                    'path': 'test/sample-1.out',
                    'data': 'foo\n'
                },
                {
                    'path': 'test/sample-2.in',
                    'data': 'bar\n'
                },
                {
                    'path': 'test/sample-2.out',
                    'data': 'foo\n'
                },
                {
                    'path': 'test/sample-3.in',
                    'data': 'foobar \n'
                },
                {
                    'path': 'test/sample-3.out',
                    'data': 'foobar\n'
                },
            ],
            expected=[{
                'status': 'AC',
                'testcase': {
                    'name': 'sample-1',
                    'input': '%s/test/sample-1.in',
                    'output': '%s/test/sample-1.out',
                },
                'output': 'foo\n',
                'exitcode': 0,
            }, {
                'status': 'WA',
                'testcase': {
                    'name': 'sample-2',
                    'input': '%s/test/sample-2.in',
                    'output': '%s/test/sample-2.out',
                },
                'output': 'bar\n',
                'exitcode': 0,
            }, {
                'status': 'AC',
                'testcase': {
                    'name': 'sample-3',
                    'input': '%s/test/sample-3.in',
                    'output': '%s/test/sample-3.out',
                },
                'output': 'foobar \n',
                'exitcode': 0,
            }],
        )

    def test_call_test_norstrip(self):
        self.snippet_call_test(
            args=['-c', cat(), '--no-rstrip'],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo \n'
                },
                {
                    'path': 'test/sample-1.out',
                    'data': 'foo\n'
                },
            ],
            expected=[{
                'status': 'WA',
                'testcase': {
                    'name': 'sample-1',
                    'input': '%s/test/sample-1.in',
                    'output': '%s/test/sample-1.out',
                },
                'output': 'foo \n',
                'exitcode': 0,
            }],
        )

    def test_call_test_float(self):
        self.snippet_call_test(
            args=['-c', cat(), '-e', '0.1'],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': '1.0\n'
                },
                {
                    'path': 'test/sample-1.out',
                    'data': '1.0001\n'
                },
                {
                    'path': 'test/sample-2.in',
                    'data': '1.0\n'
                },
                {
                    'path': 'test/sample-2.out',
                    'data': '1.2\n'
                },
                {
                    'path': 'test/sample-3.in',
                    'data': 'foo\n'
                },
                {
                    'path': 'test/sample-3.out',
                    'data': 'foo\n'
                },
                {
                    'path': 'test/sample-4.in',
                    'data': 'foo\n'
                },
                {
                    'path': 'test/sample-4.out',
                    'data': 'bar\n'
                },
                {
                    'path': 'test/sample-5.in',
                    'data': '1.0\n2.0\n'.replace('\n', os.linesep)
                },
                {
                    'path': 'test/sample-5.out',
                    'data': '1.0\n'.replace('\n', os.linesep)
                },
            ],
            expected=[{
                'status': 'AC',
                'testcase': {
                    'name': 'sample-1',
                    'input': '%s/test/sample-1.in',
                    'output': '%s/test/sample-1.out',
                },
                'output': '1.0\n',
                'exitcode': 0,
            }, {
                'status': 'WA',
                'testcase': {
                    'name': 'sample-2',
                    'input': '%s/test/sample-2.in',
                    'output': '%s/test/sample-2.out',
                },
                'output': '1.0\n',
                'exitcode': 0,
            }, {
                'status': 'AC',
                'testcase': {
                    'name': 'sample-3',
                    'input': '%s/test/sample-3.in',
                    'output': '%s/test/sample-3.out',
                },
                'output': 'foo\n',
                'exitcode': 0,
            }, {
                'status': 'WA',
                'testcase': {
                    'name': 'sample-4',
                    'input': '%s/test/sample-4.in',
                    'output': '%s/test/sample-4.out',
                },
                'output': 'foo\n',
                'exitcode': 0,
            }, {
                'status': 'WA',
                'testcase': {
                    'name': 'sample-5',
                    'input': '%s/test/sample-5.in',
                    'output': '%s/test/sample-5.out',
                },
                'output': '1.0\n2.0\n'.replace('\n', os.linesep),
                'exitcode': 0,
            }],
        )

    def test_call_test_special_judge(self):
        def assert_each_line_count(testcase_input: int, user_output: int, testcase_output: int) -> str:
            def assert_line_count(file_path: str, expected: int):
                return "with open({}, 'rb') as f:\n  assert len(f.readlines()) == {}\n".format(file_path, expected).replace('\n', os.linesep)

            return tests.utils.python_c('import sys\n{}{}{}'.format(assert_line_count('sys.argv[1]', testcase_input), assert_line_count('sys.argv[2]', user_output), assert_line_count('sys.argv[3]', testcase_output)))

        def echo(sentence: str) -> str:
            return tests.utils.python_c("import os, sys; sys.stdout.buffer.write(('{}' + os.linesep).encode())".format(sentence))

        self.snippet_call_test(
            args=['-c', echo('foo'), '--judge-command', assert_each_line_count(2, 1, 3)],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo\nfoobar\n'.replace('\n', os.linesep)
                },
                {
                    'path': 'test/sample-1.out',
                    'data': 'foo\nfoo\nfoo\n'.replace('\n', os.linesep)
                },
                {
                    'path': 'test/sample-2.in',
                    'data': 'foo\nfoobar\n'.replace('\n', os.linesep)
                },
                {
                    'path': 'test/sample-2.out',
                    'data': 'foo\nfoo\nfoo\nbar\n'.replace('\n', os.linesep)
                },
                {
                    'path': 'test/sample-3.in',
                    'data': 'foofoobar\n'.replace('\n', os.linesep)
                },
                {
                    'path': 'test/sample-3.out',
                    'data': 'foo\nfoo\nfoo\n'.replace('\n', os.linesep)
                },
            ],
            expected=[{
                'status': 'AC',
                'testcase': {
                    'name': 'sample-1',
                    'input': '%s/test/sample-1.in',
                    'output': '%s/test/sample-1.out',
                },
                'output': 'foo\n',
                'exitcode': 0,
            }, {
                'status': 'WA',
                'testcase': {
                    'name': 'sample-2',
                    'input': '%s/test/sample-2.in',
                    'output': '%s/test/sample-2.out',
                },
                'output': 'foo\n',
                'exitcode': 0,
            }, {
                'status': 'WA',
                'testcase': {
                    'name': 'sample-3',
                    'input': '%s/test/sample-3.in',
                    'output': '%s/test/sample-3.out',
                },
                'output': 'foo\n',
                'exitcode': 0,
            }],
        )

    def test_call_test_multiline_all(self):
        self.snippet_call_test(
            args=['-c', cat(), '-m', 'simple'],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo\nfoobar\n'.replace('\n', os.linesep)
                },
                {
                    'path': 'test/sample-1.out',
                    'data': 'foo\nfoobar\n'.replace('\n', os.linesep)
                },
                {
                    'path': 'test/sample-2.in',
                    'data': 'bar\nfoobar\n'.replace('\n', os.linesep)
                },
                {
                    'path': 'test/sample-2.out',
                    'data': 'bar\nbarbar\n'.replace('\n', os.linesep)
                },
            ],
            expected=[{
                'status': 'AC',
                'testcase': {
                    'name': 'sample-1',
                    'input': '%s/test/sample-1.in',
                    'output': '%s/test/sample-1.out',
                },
                'output': 'foo\nfoobar\n'.replace('\n', os.linesep),
                'exitcode': 0,
            }, {
                'status': 'WA',
                'testcase': {
                    'name': 'sample-2',
                    'input': '%s/test/sample-2.in',
                    'output': '%s/test/sample-2.out',
                },
                'output': 'bar\nfoobar\n'.replace('\n', os.linesep),
                'exitcode': 0,
            }],
        )

    def test_call_test_multiline_line(self):
        self.snippet_call_test(
            args=['-c', cat(), '-m', 'side-by-side'],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo\nfoobar\n'
                },
                {
                    'path': 'test/sample-1.out',
                    'data': 'foo\nfoobar\n'
                },
                {
                    'path': 'test/sample-2.in',
                    'data': 'bar\nfoobar\n'
                },
                {
                    'path': 'test/sample-2.out',
                    'data': 'bar\nbarbar\n'
                },
                {
                    'path': 'test/sample-3.in',
                    'data': 'bar\nfoobar\n'
                },
                {
                    'path': 'test/sample-3.out',
                    'data': 'bar\nfoobar\nbar\n'
                },
                {
                    'path': 'test/sample-4.in',
                    'data': 'bar\nfoobar\nbar\n'
                },
                {
                    'path': 'test/sample-4.out',
                    'data': 'bar\nfoobar\n'
                },
            ],
            expected=[{
                'status': 'AC',
                'testcase': {
                    'name': 'sample-1',
                    'input': '%s/test/sample-1.in',
                    'output': '%s/test/sample-1.out',
                },
                'output': 'foo\nfoobar\n',
                'exitcode': 0,
            }, {
                'status': 'WA',
                'testcase': {
                    'name': 'sample-2',
                    'input': '%s/test/sample-2.in',
                    'output': '%s/test/sample-2.out',
                },
                'output': 'bar\nfoobar\n',
                'exitcode': 0,
            }, {
                'status': 'WA',
                'testcase': {
                    'name': 'sample-3',
                    'input': '%s/test/sample-3.in',
                    'output': '%s/test/sample-3.out',
                },
                'output': 'bar\nfoobar\n',
                'exitcode': 0,
            }, {
                'status': 'WA',
                'testcase': {
                    'name': 'sample-4',
                    'input': '%s/test/sample-4.in',
                    'output': '%s/test/sample-4.out',
                },
                'output': 'bar\nfoobar\nbar\n',
                'exitcode': 0,
            }],
        )

    def test_call_test_select(self):
        self.snippet_call_test(
            args=['-c', cat(), 'test/sample-2.in', 'test/sample-3.in', 'test/sample-3.out'],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo\n'
                },
                {
                    'path': 'test/sample-1.out',
                    'data': 'Yes\n'
                },
                {
                    'path': 'test/sample-2.in',
                    'data': 'bar\n'
                },
                {
                    'path': 'test/sample-2.out',
                    'data': 'No\n'
                },
                {
                    'path': 'test/sample-3.in',
                    'data': 'baz\n'
                },
                {
                    'path': 'test/sample-3.out',
                    'data': 'No\n'
                },
            ],
            expected=[{
                'status': 'AC',
                'testcase': {
                    'name': 'sample-2',
                    'input': '%s/test/sample-2.in',
                },
                'output': 'bar\n',
                'exitcode': 0,
            }, {
                'status': 'WA',
                'testcase': {
                    'name': 'sample-3',
                    'input': '%s/test/sample-3.in',
                    'output': '%s/test/sample-3.out',
                },
                'output': 'baz\n',
                'exitcode': 0,
            }],
        )

    def test_call_test_shell(self):
        self.snippet_call_test(
            args=['-c', '{} ./build/foo.py hoge'.format(sys.executable)],
            files=[
                {
                    'path': 'build/foo.py',
                    'data': 'import sys\nprint(sys.argv[1])\n',
                    'executable': True
                },
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo\n'
                },
                {
                    'path': 'test/sample-1.out',
                    'data': 'foo\n'
                },
            ],
            expected=[{
                'status': 'WA',
                'testcase': {
                    'name': 'sample-1',
                    'input': '%s/test/sample-1.in',
                    'output': '%s/test/sample-1.out',
                },
                'output': 'hoge\n',
                'exitcode': 0,
            }],
        )

    def test_call_test_ignore_backup(self):
        self.snippet_call_test(
            args=['-c', cat()],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo\n'
                },
                {
                    'path': 'test/sample-1.in~',
                    'data': 'bar\n'
                },
                {
                    'path': 'test/sample-1.out',
                    'data': 'bar\n'
                },
                {
                    'path': 'test/sample-2.in',
                    'data': 'baz\n'
                },
                {
                    'path': 'test/sample-2.in~',
                    'data': 'bar\n'
                },
            ],
            expected=[{
                'status': 'WA',
                'testcase': {
                    'name': 'sample-1',
                    'input': '%s/test/sample-1.in',
                    'output': '%s/test/sample-1.out',
                },
                'output': 'foo\n',
                'exitcode': 0,
            }, {
                'status': 'AC',
                'testcase': {
                    'name': 'sample-2',
                    'input': '%s/test/sample-2.in',
                },
                'output': 'baz\n',
                'exitcode': 0,
            }],
        )

    @unittest.expectedFailure
    def test_call_test_no_ignore_backup(self):
        # it should be reported: [ERROR] unrecognizable file found: test/sample-1.in~
        self.snippet_call_test(
            args=['-c', cat(), '--no-ignore-backup'],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo\n'
                },
                {
                    'path': 'test/sample-1.in~',
                    'data': 'bar\n'
                },
            ],
            expected=None,
        )

    def test_call_test_dir(self):
        self.snippet_call_test(
            args=['-c', cat(), '-d', 'p/o/../../p/o/y/o'],
            files=[
                {
                    'path': 'p/o/y/o/sample-1.in',
                    'data': 'foo\n'
                },
                {
                    'path': 'p/o/y/o/sample-1.out',
                    'data': 'foo\n'
                },
                {
                    'path': 'test/sample-2.in',
                    'data': 'bar\n'
                },
                {
                    'path': 'test/sample-2.out',
                    'data': 'bar\n'
                },
            ],
            expected=[{
                'status': 'AC',
                'testcase': {
                    'name': 'sample-1',
                    'input': '%s/p/o/y/o/sample-1.in',
                    'output': '%s/p/o/y/o/sample-1.out',
                },
                'output': 'foo\n',
                'exitcode': 0,
            }],
        )

    def test_call_test_format(self):
        self.snippet_call_test(
            args=['-c', cat(), '-d', 'yuki/coder', '-f', 'test_%e/%s'],
            files=[
                {
                    'path': 'yuki/coder/test_in/sample-1.txt',
                    'data': 'foo\n'
                },
                {
                    'path': 'yuki/coder/test_out/sample-1.txt',
                    'data': 'foo\n'
                },
                {
                    'path': 'test_in/sample-2.in',
                    'data': 'bar\n'
                },
                {
                    'path': 'test_out/sample-2.out',
                    'data': 'bar\n'
                },
            ],
            expected=[{
                'status': 'AC',
                'testcase': {
                    'name': 'sample-1.txt',
                    'input': '%s/yuki/coder/test_in/sample-1.txt',
                    'output': '%s/yuki/coder/test_out/sample-1.txt',
                },
                'output': 'foo\n',
                'exitcode': 0,
            }],
        )

    def test_call_test_format_select(self):
        self.snippet_call_test(
            args=['-c', cat(), '-d', 'yuki/coder', '-f', 'test_%e/%s', 'yuki/coder/test_in/sample-2.txt', 'yuki/coder/test_in/sample-3.txt', 'yuki/coder/test_out/sample-3.txt'],
            files=[
                {
                    'path': 'yuki/coder/test_in/sample-1.txt',
                    'data': 'foo\n'
                },
                {
                    'path': 'yuki/coder/test_out/sample-1.txt',
                    'data': 'foo\n'
                },
                {
                    'path': 'yuki/coder/test_in/sample-2.txt',
                    'data': 'bar\n'
                },
                {
                    'path': 'yuki/coder/test_out/sample-2.txt',
                    'data': 'bar\n'
                },
                {
                    'path': 'yuki/coder/test_in/sample-3.txt',
                    'data': 'baz\n'
                },
                {
                    'path': 'yuki/coder/test_out/sample-3.txt',
                    'data': 'baz\n'
                },
            ],
            expected=[{
                'status': 'AC',
                'testcase': {
                    'name': 'sample-2.txt',
                    'input': '%s/yuki/coder/test_in/sample-2.txt',
                },
                'output': 'bar\n',
                'exitcode': 0,
            }, {
                'status': 'AC',
                'testcase': {
                    'name': 'sample-3.txt',
                    'input': '%s/yuki/coder/test_in/sample-3.txt',
                    'output': '%s/yuki/coder/test_out/sample-3.txt',
                },
                'output': 'baz\n',
                'exitcode': 0,
            }],
        )

    def test_call_test_format_hack(self):
        self.snippet_call_test(
            args=['-c', cat(), '-d', 'a/b', '-f', 'c/test_%e/d/%s/e.case.txt'],
            files=[
                {
                    'path': 'a/b/c/test_in/d/sample.case.1/e.case.txt',
                    'data': 'foo\n'
                },
                {
                    'path': 'a/b/c/test_out/d/sample.case.1/e.case.txt',
                    'data': 'foo\n'
                },
                {
                    'path': 'a/b/c/test_in/d/sample.case.2/e.case.txt',
                    'data': 'bar\n'
                },
                {
                    'path': 'a/b/c/test_out/d/sample.case.2/e.case.txt',
                    'data': 'bar\n'
                },
            ],
            expected=[{
                'status': 'AC',
                'testcase': {
                    'name': 'sample.case.1',
                    'input': '%s/a/b/c/test_in/d/sample.case.1/e.case.txt',
                    'output': '%s/a/b/c/test_out/d/sample.case.1/e.case.txt',
                },
                'output': 'foo\n',
                'exitcode': 0,
            }, {
                'status': 'AC',
                'testcase': {
                    'name': 'sample.case.2',
                    'input': '%s/a/b/c/test_in/d/sample.case.2/e.case.txt',
                    'output': '%s/a/b/c/test_out/d/sample.case.2/e.case.txt',
                },
                'output': 'bar\n',
                'exitcode': 0,
            }],
        )

    @unittest.skipIf(os.name == 'nt', "character '*' is not usable for paths in Windows")
    def test_call_test_re_glob_injection(self):
        self.snippet_call_test(
            args=['-c', cat(), '-d', 'a.*/[abc]/**', '-f', '***/**/def/test_%e/%s.txt'],
            files=[
                {
                    'path': 'a.*/[abc]/**/***/**/def/test_in/1.txt',
                    'data': 'foo\n'
                },
                {
                    'path': 'a.*/[abc]/**/***/**/def/test_out/1.txt',
                    'data': 'foo\n'
                },
                {
                    'path': 'a.*/a/**/**/**/def/test_in/2.txt',
                    'data': 'bar\n'
                },
                {
                    'path': 'a.*/[abc]/**/**/**/def/test_out/2.txt',
                    'data': 'bar\n'
                },
            ],
            expected=[{
                'status': 'AC',
                'testcase': {
                    'name': '1',
                    'input': '%s/a.*/[abc]/**/***/**/def/test_in/1.txt',
                    'output': '%s/a.*/[abc]/**/***/**/def/test_out/1.txt',
                },
                'output': 'foo\n',
                'exitcode': 0,
            }],
        )

    def test_call_test_in_parallel(self):
        TOTAL = 100
        PARALLEL = 32
        files = []
        expected = []
        for i in range(TOTAL):
            name = 'sample-%03d' % i
            files += [{
                'path': 'test/{}.in'.format(name),
                'data': '{}\n'.format(i),
            }]
            files += [{
                'path': 'test/{}.out'.format(name),
                'data': '{}\n'.format(i),
            }]
            expected += [{
                'status': 'AC' if i == 1 else 'WA',
                'testcase': {
                    'name': name,
                    'input': '%s/test/{}.in'.format(name),
                    'output': '%s/test/{}.out'.format(name),
                },
                'output': '1\n',
                'exitcode': 0,
            }]
        self.snippet_call_test(
            args=['--jobs', str(PARALLEL), '--silent', '-c', tests.utils.python_c("import time; time.sleep(1); print(1)")],
            files=files,
            expected=expected,
            verbose=False,
        )

    def test_call_test_tle(self):
        data = self.snippet_call_test(
            args=['-c', sleep_1sec(), '-t', '0.1'],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo\n'
                },
            ],
            expected=None,
        )
        for case in data:
            self.assertEqual(case['status'], 'TLE')

    def test_call_test_not_tle(self):
        data = self.snippet_call_test(
            args=['-c', sleep_1sec(), '-t', '2.0'],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo\n'
                },
            ],
            expected=None,
        )
        for case in data:
            self.assertEqual(case['status'], 'AC')

    @unittest.skipIf(os.name == 'nt', "memory checking is disabled on Windows environment")
    def test_call_test_large_memory(self):
        # make a bytes of 100 MB
        data = self.snippet_call_test(
            args=['-c', tests.utils.python_c("print(len(b'A' * 100000000))")],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo\n'
                },
            ],
            expected=None,
        )
        for case in data:
            self.assertEqual(case['status'], 'AC')
            self.assertGreater(case['memory'], 100)
            self.assertLess(case['memory'], 1000)

    @unittest.skipIf(os.name == 'nt', "memory checking is disabled on Windows environment")
    def test_call_test_small_memory(self):
        # just print "foo"
        data = self.snippet_call_test(
            args=['-c', tests.utils.python_c("print('foo')")],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo\n'
                },
            ],
            expected=None,
        )
        for case in data:
            self.assertEqual(case['status'], 'AC')
            self.assertLess(case['memory'], 100)

    @unittest.skipIf(os.name == 'nt', "memory checking is disabled on Windows environment")
    def test_call_test_memory_limit_error(self):
        # make a bytes of 100 MB
        self.snippet_call_test(
            args=['--mle', '50', '-c', tests.utils.python_c("print(len(b'A' * 100000000))")],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo\n'
                },
            ],
            expected=[{
                'status': 'MLE',
                'testcase': {
                    'name': 'sample-1',
                    'input': '%s/test/sample-1.in',
                },
                'output': '100000000\n',
                'exitcode': 0,
            }],
        )

    def test_call_stderr(self):
        data = self.snippet_call_test(
            args=['-c', tests.utils.python_c("import sys; print('foo', file=sys.stderr)")],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo\n'
                },
            ],
            expected=[{
                'status': 'AC',
                'testcase': {
                    'name': 'sample-1',
                    'input': '%s/test/sample-1.in',
                },
                'output': '',
                'exitcode': 0,
            }],
        )

    def test_call_runtime_error(self):
        data = self.snippet_call_test(
            args=['-c', tests.utils.python_c("exit(1)")],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo\n'
                },
            ],
            expected=[{
                'status': 'RE',
                'testcase': {
                    'name': 'sample-1',
                    'input': '%s/test/sample-1.in',
                },
                'output': '',
                'exitcode': 1,
            }],
        )

    def test_call_stderr_and_fail(self):
        data = self.snippet_call_test(
            args=['-c', tests.utils.python_c("import sys; print('good bye', file=sys.stderr); exit(255)")],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo\n'
                },
                {
                    'path': 'test/sample-1.out',
                    'data': 'foo\n'
                },
            ],
            expected=[{
                'status': 'WA',
                'testcase': {
                    'name': 'sample-1',
                    'input': '%s/test/sample-1.in',
                    'output': '%s/test/sample-1.out',
                },
                'output': '',
                'exitcode': 255,
            }],
        )

    def test_call_non_unicode(self):
        data = self.snippet_call_test(
            args=['-c', tests.utils.python_c("import sys; sys.stdout.buffer.write(bytes(range(256)))")],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo\n'
                },
            ],
            expected=[{
                'status': 'AC',
                'testcase': {
                    'name': 'sample-1',
                    'input': '%s/test/sample-1.in',
                },
                'output': bytes(range(256)).decode(errors='replace'),
                'exitcode': 0,
            }],
        )

    # TODO: fix
    @unittest.expectedFailure
    @unittest.skipIf(os.name == 'nt', "procfs is required")
    def test_call_test_check_no_zombie(self):
        marker = 'zombie-%08x' % random.randrange(2**32)
        data = self.snippet_call_test(
            args=['-c', tests.utils.python_c("import time; time.sleep(100)  # {}".format(marker)), '--tle', '1'],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': 'foo\n'
                },
                {
                    'path': 'test/sample-2.in',
                    'data': 'foo\n'
                },
            ],
            expected=[{
                'status': 'TLE',
                'testcase': {
                    'name': 'sample-1',
                    'input': '%s/test/sample-1.in',
                },
                'output': '',
                'exitcode': None,
            }, {
                'status': 'TLE',
                'testcase': {
                    'name': 'sample-2',
                    'input': '%s/test/sample-2.in',
                },
                'output': '',
                'exitcode': None,
            }],
        )
        # check there are no processes whose command-line arguments contains the marker word
        for cmdline in pathlib.Path('/proc').glob('*/cmdline'):
            with open(str(cmdline), 'rb') as fh:
                self.assertNotIn(marker.encode(), fh.read())


@unittest.skipIf(os.name == 'nt', "memory checking is disabled and output is different with Linux")
class TestTestLog(unittest.TestCase):
    max_chars = shutil.get_terminal_size()[0] // 2 - 2

    def check_log_lines(self, result, expect):
        self.assertEqual(len(result), len(expect))
        for result_line, expect_line in zip(result, expect):
            if expect_line.startswith('[x]'):
                # Time and max memory can not be reproduced
                self.assertTrue(result_line.startswith(expect_line))
            else:
                self.assertEqual(result_line, expect_line)

    def snippet_call_test(self, args, files, expected_log_lines):
        self.maxDiff = None
        result = tests.utils.run_in_sandbox(args=['test'] + args, files=files, pipe_stderr=True)
        print(result['proc'].stderr.decode(), file=sys.stderr)
        self.check_log_lines(result['proc'].stderr.decode().split(os.linesep), expected_log_lines)

    def test_trailing_spaces(self):
        self.snippet_call_test(
            args=['-c', tests.utils.python_c(r"import sys; sys.stdout.buffer.write(b'1\r\n2 \r\n3\n4  \t  \n5  \n6')")],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': '',
                },
                {
                    'path': 'test/sample-1.out',
                    'data': '1\n2\n3\n',
                },
            ],
            expected_log_lines=[
                '[*] 1 cases found',
                '',
                '[*] sample-1',
                '[x] time:',
                '[-] WA',
                'output:',
                r'1\r',
                r'2_\r(trailing spaces)',
                r'3',
                r'4__\t__(trailing spaces)',
                r'5__(trailing spaces)',
                r'6(no trailing newline)',
                'expected:',
                '1',
                '2',
                '3',
                '',
                '',
                '[x] slowest:',
                '[x] max memory:',
                '[-] test failed: 0 AC / 1 cases',
                '',
            ],
        )

    def test_side_by_short(self):
        self.snippet_call_test(
            args=['-m', 'side-by-side', '-c', cat(), '--no-rstrip'],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': os.linesep * 4 + '1' + os.linesep * 4
                },
                {
                    'path': 'test/sample-1.out',
                    'data': os.linesep * 4 + '2' + os.linesep * 4
                },
            ],
            expected_log_lines=[
                '[*] 1 cases found',
                '',
                '[*] sample-1',
                '[x] time:',
                '[-] WA',
                'output:' + ' ' * (self.max_chars - 7) + '|expected:',
                '-' * self.max_chars + '|' + '-' * self.max_chars,
                ' ' * self.max_chars + '|',
                ' ' * self.max_chars + '|',
                ' ' * self.max_chars + '|',
                ' ' * self.max_chars + '|',
                '1' + ' ' * (self.max_chars - 1) + '|2',
                ' ' * self.max_chars + '|',
                ' ' * self.max_chars + '|',
                ' ' * self.max_chars + '|',
                ' ' * self.max_chars + '|',
                '',
                '[x] slowest:',
                '[x] max memory:',
                '[-] test failed: 0 AC / 1 cases',
                '',
            ],
        )

    def test_side_by_side_long1(self):
        self.snippet_call_test(
            args=['-m', 'side-by-side', '-c', cat(), '--no-rstrip'],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': os.linesep * 40 + '1' + os.linesep * 10
                },
                {
                    'path': 'test/sample-1.out',
                    'data': os.linesep * 40 + '2' + os.linesep * 10
                },
            ],
            expected_log_lines=[
                '[*] 1 cases found',
                '',
                '[*] sample-1',
                '[x] ',
                '[-] WA',
                '  |output:' + ' ' * (self.max_chars - 10) + '|expected:',
                '-' * self.max_chars + '|' + '-' * self.max_chars,
                '38|' + ' ' * (self.max_chars - 3) + '|',
                '39|' + ' ' * (self.max_chars - 3) + '|',
                '40|' + ' ' * (self.max_chars - 3) + '|',
                '41|1' + ' ' * (self.max_chars - 4) + '|2',
                '42|' + ' ' * (self.max_chars - 3) + '|',
                '43|' + ' ' * (self.max_chars - 3) + '|',
                '44|' + ' ' * (self.max_chars - 3) + '|',
                '... (7 lines) ...',
                '',
                '[x] slowest:',
                '[x] max memory:',
                '[-] test failed: 0 AC / 1 cases',
                '',
            ],
        )

    def test_side_by_side_long2(self):
        self.snippet_call_test(
            args=['-m', 'side-by-side', '-c', cat(), '--no-rstrip'],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': os.linesep * 50 + '1'
                },
                {
                    'path': 'test/sample-1.out',
                    'data': os.linesep * 50 + '2'
                },
            ],
            expected_log_lines=[
                '[*] 1 cases found',
                '',
                '[*] sample-1',
                '[x] ',
                '[-] WA',
                '  |output:' + ' ' * (self.max_chars - 10) + '|expected:',
                '-' * self.max_chars + '|' + '-' * self.max_chars,
                '45|' + ' ' * (self.max_chars - 3) + '|',
                '46|' + ' ' * (self.max_chars - 3) + '|',
                '47|' + ' ' * (self.max_chars - 3) + '|',
                '48|' + ' ' * (self.max_chars - 3) + '|',
                '49|' + ' ' * (self.max_chars - 3) + '|',
                '50|' + ' ' * (self.max_chars - 3) + '|',
                '51|1                                  |2',
                '',
                '[x] slowest:',
                '[x] max memory:',
                '[-] test failed: 0 AC / 1 cases',
                '',
            ],
        )

    def test_side_by_side_long3(self):
        self.snippet_call_test(
            args=['-m', 'side-by-side', '-c', cat(), '--no-rstrip'],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': os.linesep * 40 + ('1' + os.linesep) * 10
                },
                {
                    'path': 'test/sample-1.out',
                    'data': os.linesep * 40 + ('1' + os.linesep) * 5 + '2' + os.linesep + ('1' + os.linesep) * 5
                },
            ],
            expected_log_lines=[
                '[*] 1 cases found',
                '',
                '[*] sample-1',
                '[x] ',
                '[-] WA',
                '  |output:' + ' ' * (self.max_chars - 10) + '|expected:',
                '-' * self.max_chars + '|' + '-' * self.max_chars,
                '43|1' + ' ' * (self.max_chars - 4) + '|1',
                '44|1' + ' ' * (self.max_chars - 4) + '|1',
                '45|1' + ' ' * (self.max_chars - 4) + '|1',
                '  |' + ' ' * (self.max_chars - 3) + '|2',
                '46|1' + ' ' * (self.max_chars - 4) + '|1',
                '47|1' + ' ' * (self.max_chars - 4) + '|1',
                '48|1' + ' ' * (self.max_chars - 4) + '|1',
                '... (3 lines) ...',
                '',
                '[x] slowest:',
                '[x] max memory:',
                '[-] test failed: 0 AC / 1 cases',
                '',
            ],
        )

    def test_side_by_side_long4(self):
        self.snippet_call_test(
            args=['-m', 'side-by-side', '-c', cat(), '--no-rstrip'],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': os.linesep * 40 + ('1' + os.linesep) * 5 + '2' + os.linesep + ('1' + os.linesep) * 5
                },
                {
                    'path': 'test/sample-1.out',
                    'data': os.linesep * 40 + ('1' + os.linesep) * 10
                },
            ],
            expected_log_lines=[
                '[*] 1 cases found',
                '',
                '[*] sample-1',
                '[x] ',
                '[-] WA',
                '  |output:' + ' ' * (self.max_chars - 10) + '|expected:',
                '-' * self.max_chars + '|' + '-' * self.max_chars,
                '43|1' + ' ' * (self.max_chars - 4) + '|1',
                '44|1' + ' ' * (self.max_chars - 4) + '|1',
                '45|1' + ' ' * (self.max_chars - 4) + '|1',
                '46|2' + ' ' * (self.max_chars - 4) + '|',
                '47|1' + ' ' * (self.max_chars - 4) + '|1',
                '48|1' + ' ' * (self.max_chars - 4) + '|1',
                '49|1' + ' ' * (self.max_chars - 4) + '|1',
                '... (3 lines) ...',
                '',
                '[x] slowest:',
                '[x] max memory:',
                '[-] test failed: 0 AC / 1 cases',
                '',
            ],
        )

    def test_side_by_side_long5(self):
        self.snippet_call_test(
            args=['-m', 'side-by-side', '-c', cat(), '--no-rstrip'],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': os.linesep * 40 + ('1' + os.linesep) * 11
                },
                {
                    'path': 'test/sample-1.out',
                    'data': os.linesep * 40 + ('1' + os.linesep) * 5 + '1 2' + os.linesep + ('1' + os.linesep) * 5
                },
            ],
            expected_log_lines=[
                '[*] 1 cases found',
                '',
                '[*] sample-1',
                '[x] ',
                '[-] WA',
                '  |output:' + ' ' * (self.max_chars - 10) + '|expected:',
                '-' * self.max_chars + '|' + '-' * self.max_chars,
                '43|1' + ' ' * (self.max_chars - 4) + '|1',
                '44|1' + ' ' * (self.max_chars - 4) + '|1',
                '45|1' + ' ' * (self.max_chars - 4) + '|1',
                '46|1' + ' ' * (self.max_chars - 4) + '|1 2',
                '47|1' + ' ' * (self.max_chars - 4) + '|1',
                '48|1' + ' ' * (self.max_chars - 4) + '|1',
                '49|1' + ' ' * (self.max_chars - 4) + '|1',
                '... (3 lines) ...',
                '',
                '[x] slowest:',
                '[x] max memory:',
                '[-] test failed: 0 AC / 1 cases',
                '',
            ],
        )

    def test_side_by_side_long6(self):
        self.snippet_call_test(
            args=['-m', 'side-by-side', '-c', cat(), '--no-rstrip'],
            files=[
                {
                    'path': 'test/sample-1.in',
                    'data': os.linesep * 40 + ('1' + os.linesep) * 5 + '1 2' + os.linesep + ('1' + os.linesep) * 5
                },
                {
                    'path': 'test/sample-1.out',
                    'data': os.linesep * 40 + ('1' + os.linesep) * 11
                },
            ],
            expected_log_lines=[
                '[*] 1 cases found',
                '',
                '[*] sample-1',
                '[x] ',
                '[-] WA',
                '  |output:' + ' ' * (self.max_chars - 10) + '|expected:',
                '-' * self.max_chars + '|' + '-' * self.max_chars,
                '43|1' + ' ' * (self.max_chars - 4) + '|1',
                '44|1' + ' ' * (self.max_chars - 4) + '|1',
                '45|1' + ' ' * (self.max_chars - 4) + '|1',
                '46|1 2' + ' ' * (self.max_chars - 6) + '|1',
                '47|1' + ' ' * (self.max_chars - 4) + '|1',
                '48|1' + ' ' * (self.max_chars - 4) + '|1',
                '49|1' + ' ' * (self.max_chars - 4) + '|1',
                '... (3 lines) ...',
                '',
                '[x] slowest:',
                '[x] max memory:',
                '[-] test failed: 0 AC / 1 cases',
                '',
            ],
        )


class TestTestSideBySideLog(unittest.TestCase):
    max_chars = shutil.get_terminal_size()[0] // 2 - 2

    def snippet_call_test(self, answer, expected, display_lines):
        lines = [
            ('onlinejudge._implementation.logging', 'INFO', 'output:' + ' ' * (self.max_chars - 7) + '|expected:'),
            ('onlinejudge._implementation.logging', 'INFO', '-' * self.max_chars + '|' + '-' * self.max_chars),
        ]
        for line in display_lines:
            lines.append(('onlinejudge._implementation.logging', 'INFO', line))

        with LogCapture() as capture:
            test.display_side_by_side_color(answer, expected)
            capture.check(*lines)

    def test_side_by_side1(self):
        self.snippet_call_test('kmyk', 'kmyk', ('kmyk' + ' ' * (self.max_chars - 4) + '|kmyk', ))

    def test_side_by_side2(self):
        self.snippet_call_test('kmy', 'kmv', (logging.red('km' + logging.red_diff('y') + ' ' * (self.max_chars - 3)) + '|' + logging.green('km' + logging.green_diff('v')), ))

    def test_side_by_side3(self):
        display_lines = [
            'Alice' + ' ' * (self.max_chars - 5) + '|Alice',
            'Bob' + ' ' * (self.max_chars - 3) + '|Bob',
            'Alice' + ' ' * (self.max_chars - 5) + '|Alice',
        ]
        self.snippet_call_test('Alice\nBob\nAlice', 'Alice\nBob\nAlice', display_lines)

    def test_side_by_side4(self):
        display_lines = [
            'Alice' + ' ' * (self.max_chars - 5) + '|Alice',
            logging.red('B' + logging.red_diff('0') + 'b' + ' ' * (self.max_chars - 3)) + '|' + logging.green('B' + logging.green_diff('o') + 'b'),
            'Alice' + ' ' * (self.max_chars - 5) + '|Alice',
        ]
        self.snippet_call_test('Alice\nB0b\nAlice', 'Alice\nBob\nAlice', display_lines)

    def test_side_by_side5(self):
        display_lines = [
            logging.red(' ' * (self.max_chars)) + '|' + logging.green(logging.green_diff('0 2')),
            '1 2' + ' ' * (self.max_chars - 3) + '|1 2',
            '2 2' + ' ' * (self.max_chars - 3) + '|2 2',
            '3 2' + ' ' * (self.max_chars - 3) + '|3 2',
            logging.red(logging.red_diff('4 2') + ' ' * (self.max_chars - 3)) + '|' + logging.green(''),
        ]
        self.snippet_call_test('1 2\n2 2\n3 2\n4 2', '0 2\n1 2\n2 2\n3 2', display_lines)

    def test_side_by_side6(self):
        display_lines = [
            logging.red(' ' * (self.max_chars)) + '|' + logging.green(logging.green_diff('0 2')),
            logging.red(' ' * (self.max_chars)) + '|' + logging.green(logging.green_diff('1 2')),
            '2 2' + ' ' * (self.max_chars - 3) + '|2 2',
            '3 2' + ' ' * (self.max_chars - 3) + '|3 2',
            '4 2' + ' ' * (self.max_chars - 3) + '|4 2',
            logging.red(logging.red_diff('5 2') + ' ' * (self.max_chars - 3)) + '|' + logging.green(''),
            logging.red(logging.red_diff('6 2') + ' ' * (self.max_chars - 3)) + '|' + logging.green(''),
        ]
        self.snippet_call_test('2 2\n3 2\n4 2\n5 2\n6 2', '0 2\n1 2\n2 2\n3 2\n4 2', display_lines)

    def test_side_by_side7(self):
        display_lines = [
            logging.red(logging.red_diff('0 2') + ' ' * (self.max_chars - 3)) + '|' + logging.green(''),
            logging.red(logging.red_diff('1 2') + ' ' * (self.max_chars - 3)) + '|' + logging.green(''),
            '2 2' + ' ' * (self.max_chars - 3) + '|2 2',
            '3 2' + ' ' * (self.max_chars - 3) + '|3 2',
            '4 2' + ' ' * (self.max_chars - 3) + '|4 2',
            logging.red(' ' * (self.max_chars)) + '|' + logging.green(logging.green_diff('5 2')),
            logging.red(' ' * (self.max_chars)) + '|' + logging.green(logging.green_diff('6 2')),
        ]
        self.snippet_call_test('0 2\n1 2\n2 2\n3 2\n4 2', '2 2\n3 2\n4 2\n5 2\n6 2', display_lines)

    def test_side_by_side8(self):
        display_lines = [
            logging.red(logging.red_diff('1') + ' 0 2' + ' ' * (self.max_chars - 5)) + '|' + logging.green(logging.green_diff('2') + ' 0 2'),
            logging.red('1 ' + logging.red_diff('0') + ' 2' + ' ' * (self.max_chars - 5)) + '|' + logging.green('1 ' + logging.green_diff('1') + ' 2'),
            logging.red('1 0 ' + logging.red_diff('2') + ' ' * (self.max_chars - 5)) + '|' + logging.green('1 0 ' + logging.green_diff('3')),
        ]
        self.snippet_call_test('1 0 2\n1 0 2\n1 0 2', '2 0 2\n1 1 2\n1 0 3', display_lines)


class TestTestSnippedSideBySideLog(unittest.TestCase):
    max_chars = shutil.get_terminal_size()[0] // 2 - 2

    def snippet_call_test(self, answer, expected, display_lines, max_line_num_digits):
        lines = [
            ('onlinejudge._implementation.logging', 'INFO', " " * max_line_num_digits + '|output:' + ' ' * (self.max_chars - 8 - max_line_num_digits) + '|expected:'),
            ('onlinejudge._implementation.logging', 'INFO', '-' * self.max_chars + '|' + '-' * self.max_chars),
        ]
        for line in display_lines:
            lines.append(('onlinejudge._implementation.logging', 'INFO', line))

        with LogCapture() as capture:
            test.display_snipped_side_by_side_color(answer, expected)
            capture.check(*lines)

    def test_side_by_side1(self):
        display_lines = [
            '41|Alice' + ' ' * (self.max_chars - 8) + '|Alice',
            '42|Bob' + ' ' * (self.max_chars - 6) + '|Bob',
            '43|Alice' + ' ' * (self.max_chars - 8) + '|Alice',
            '44|' + logging.red(logging.red_diff('Bob') + ' ' * (self.max_chars - 6)) + '|' + logging.green(logging.green_diff('John')),
            '45|' + logging.red(logging.red_diff('Alice') + ' ' * (self.max_chars - 8)) + '|' + logging.green(logging.green_diff('John')),
            '46|Bob' + ' ' * (self.max_chars - 6) + '|Bob',
            '47|Alice' + ' ' * (self.max_chars - 8) + '|Alice',
            '... (1 lines) ...',
        ]
        output = ('\n' * 40 + 'Alice\nBob\nAlice\nBob\nAlice\nBob\nAlice\nBob').replace('\n', os.linesep)
        expect = ('\n' * 40 + 'Alice\nBob\nAlice\nJohn\nJohn\nBob\nAlice\nBob').replace('\n', os.linesep)
        self.snippet_call_test(output, expect, display_lines, 2)

    def test_side_by_side2(self):
        display_lines = [
            '98 |Alice' + ' ' * (self.max_chars - 9) + '|Alice',
            '99 |Bob' + ' ' * (self.max_chars - 7) + '|Bob',
            '100|Alice' + ' ' * (self.max_chars - 9) + '|Alice',
            '101|' + logging.red(logging.red_diff('Bob') + ' ' * (self.max_chars - 7)) + '|' + logging.green(logging.green_diff('John')),
            '102|' + logging.red(logging.red_diff('Alice') + ' ' * (self.max_chars - 9)) + '|' + logging.green(logging.green_diff('John')),
            '103|Bob' + ' ' * (self.max_chars - 7) + '|Bob',
            '104|Alice' + ' ' * (self.max_chars - 9) + '|Alice',
            '... (1 lines) ...',
        ]
        output = ('\n' * 97 + 'Alice\nBob\nAlice\nBob\nAlice\nBob\nAlice\nBob').replace('\n', os.linesep)
        expect = ('\n' * 97 + 'Alice\nBob\nAlice\nJohn\nJohn\nBob\nAlice\nBob').replace('\n', os.linesep)
        self.snippet_call_test(output, expect, display_lines, 3)
