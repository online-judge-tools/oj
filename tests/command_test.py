import json
import unittest

import tests.utils


class TestTest(unittest.TestCase):
    def snippet_call_test(self, args, files, expected):
        result = tests.utils.run_in_sandbox(
            args=['-v', 'test', '--json'] + args, files=files)
        self.assertTrue(result['proc'].stdout)
        data = json.loads(result['proc'].stdout.decode())
        self.assertEqual(len(data), len(expected))
        for a, b in zip(data, expected):
            self.assertEqual(a['testcase']['name'], b['testcase']['name'])
            self.assertEqual(a['testcase']['input'],
                             b['testcase']['input'] % result['tempdir'])
            self.assertEqual('output' in a['testcase'],
                             'output' in b['testcase'])
            if 'output' in b['testcase']:
                self.assertEqual(a['testcase']['output'],
                                 b['testcase']['output'] % result['tempdir'])
            self.assertEqual(a['exitcode'], b['exitcode'])
            self.assertEqual(a['result'], b['result'])
            self.assertEqual(a['output'], b['output'])

    def test_call_test_simple(self):
        self.snippet_call_test(
            args=['-c', 'cat'],
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
            ],
            expected=[{
                'result': 'AC',
                'testcase': {
                    'name': 'sample-1',
                    'input': '%s/test/sample-1.in',
                    'output': '%s/test/sample-1.out',
                },
                'output': 'foo\n',
                'exitcode': 0,
            },
                      {
                          'result': 'WA',
                          'testcase': {
                              'name': 'sample-2',
                              'input': '%s/test/sample-2.in',
                              'output': '%s/test/sample-2.out',
                          },
                          'output': 'bar\n',
                          'exitcode': 0,
                      }],
        )

    def test_call_test_select(self):
        self.snippet_call_test(
            args=[
                '-c', 'cat', 'test/sample-2.in', 'test/sample-3.in',
                'test/sample-3.out'
            ],
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
                'result': 'AC',
                'testcase': {
                    'name': 'sample-2',
                    'input': '%s/test/sample-2.in',
                },
                'output': 'bar\n',
                'exitcode': 0,
            },
                      {
                          'result': 'WA',
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
            args=['-c', './build/foo.sh hoge'],
            files=[
                {
                    'path': 'build/foo.sh',
                    'data': '#!/bin/sh\necho $1\n',
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
                'result': 'WA',
                'testcase': {
                    'name': 'sample-1',
                    'input': '%s/test/sample-1.in',
                    'output': '%s/test/sample-1.out',
                },
                'output': 'hoge\n',
                'exitcode': 0,
            }],
        )

    def test_call_test_fail(self):
        self.snippet_call_test(
            args=['-c', './foo.sh'],
            files=[
                {
                    'path': 'foo.sh',
                    'data': '#!/bin/sh\necho bar\nexit 3\n',
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
                'result': 'WA',
                'testcase': {
                    'name': 'sample-1',
                    'input': '%s/test/sample-1.in',
                    'output': '%s/test/sample-1.out',
                },
                'output': 'bar\n',
                'exitcode': 3,
            }],
        )

    def test_call_test_dir(self):
        self.snippet_call_test(
            args=['-c', 'cat', '-d', 'p/o/../../p/o/y/o'],
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
                'result': 'AC',
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
            args=['-c', 'cat', '-d', 'yuki/coder', '-f', 'test_%e/%s'],
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
                'result': 'AC',
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
            args=[
                '-c', 'cat', '-d', 'yuki/coder', '-f', 'test_%e/%s',
                'yuki/coder/test_in/sample-2.txt',
                'yuki/coder/test_in/sample-3.txt',
                'yuki/coder/test_out/sample-3.txt'
            ],
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
                'result': 'AC',
                'testcase': {
                    'name': 'sample-2.txt',
                    'input': '%s/yuki/coder/test_in/sample-2.txt',
                },
                'output': 'bar\n',
                'exitcode': 0,
            },
                      {
                          'result': 'AC',
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
            args=['-c', 'cat', '-d', 'a/b', '-f', 'c/test_%e/d/%s/e.case.txt'],
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
                'result': 'AC',
                'testcase': {
                    'name': 'sample.case.1',
                    'input': '%s/a/b/c/test_in/d/sample.case.1/e.case.txt',
                    'output': '%s/a/b/c/test_out/d/sample.case.1/e.case.txt',
                },
                'output': 'foo\n',
                'exitcode': 0,
            },
                      {
                          'result': 'AC',
                          'testcase': {
                              'name':
                              'sample.case.2',
                              'input':
                              '%s/a/b/c/test_in/d/sample.case.2/e.case.txt',
                              'output':
                              '%s/a/b/c/test_out/d/sample.case.2/e.case.txt',
                          },
                          'output': 'bar\n',
                          'exitcode': 0,
                      }],
        )
