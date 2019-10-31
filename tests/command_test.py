import json
import os
import sys
import unittest

import tests.utils
from tests.utils import cat, sleep_1sec


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
        def assert_line_count(expected: int) -> str:
            return '{} -c "import sys; assert len(sys.stdin.readlines()) == {}"'.format(sys.executable, expected)

        self.snippet_call_test(
            args=['-c', 'echo foo', '--judge-command', assert_line_count(3)],
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
                    'data': 'foo\nfoobar\n'.replace('\n', os.linesep)
                },
                {
                    'path': 'test/sample-2.out',
                    'data': 'foo\nbarbar\n'.replace('\n', os.linesep)
                },
                {
                    'path': 'test/sample-3.in',
                    'data': 'foo\nfoobar\nfoofoofoo\n'.replace('\n', os.linesep)
                },
                {
                    'path': 'test/sample-3.out',
                    'data': 'foo\nfoobar\nfoofoofoo\n'.replace('\n', os.linesep)
                },
            ],
            expected=[{
                'status': 'AC',
                'testcase': {
                    'name': 'sample-1',
                    'input': '%s/test/sample-1.in',
                    'output': '%s/test/sample-1.out',
                },
                'output': 'foo\n'.replace('\n', os.linesep),
                'exitcode': 0,
            }, {
                'status': 'AC',
                'testcase': {
                    'name': 'sample-2',
                    'input': '%s/test/sample-2.in',
                    'output': '%s/test/sample-2.out',
                },
                'output': 'foo\n'.replace('\n', os.linesep),
                'exitcode': 0,
            }, {
                'status': 'WA',
                'testcase': {
                    'name': 'sample-3',
                    'input': '%s/test/sample-3.in',
                    'output': '%s/test/sample-3.out',
                },
                'output': 'foo\n'.replace('\n', os.linesep),
                'exitcode': 0,
            }],
        )

    def test_call_test_multiline_all(self):
        self.snippet_call_test(
            args=['-c', cat(), '-m', 'all'],
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
            args=['-c', cat(), '-m', 'line'],
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
