import os
import shutil
import sys
import unittest

import tests.utils
from onlinejudge_command import logging
from onlinejudge_command.subcommand import test
from testfixtures import LogCapture
from tests.utils import cat


@unittest.skipIf(os.name == 'nt', "memory checking is disabled and output is different with Linux")
class TestTestSideBySideLogWithMemoryChecking(unittest.TestCase):
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
            ('onlinejudge_command.logging', 'INFO', 'output:' + ' ' * (self.max_chars - 7) + '|expected:'),
            ('onlinejudge_command.logging', 'INFO', '-' * self.max_chars + '|' + '-' * self.max_chars),
        ]
        for line in display_lines:
            lines.append(('onlinejudge_command.logging', 'INFO', line))

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
            ('onlinejudge_command.logging', 'INFO', " " * max_line_num_digits + '|output:' + ' ' * (self.max_chars - 8 - max_line_num_digits) + '|expected:'),
            ('onlinejudge_command.logging', 'INFO', '-' * self.max_chars + '|' + '-' * self.max_chars),
        ]
        for line in display_lines:
            lines.append(('onlinejudge_command.logging', 'INFO', line))

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
