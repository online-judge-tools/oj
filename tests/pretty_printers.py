"""This module has unit tests for onlinejudge_command.pretty_printers module.
"""

import unittest
from typing import *

from onlinejudge_command.pretty_printers import _PrettyToken, _PrettyTokenType, _render_tokens, _tokenize_file_content_without_snipping, _tokenize_large_file_content, _tokenize_line


class TokenizeLineTest(unittest.TestCase):
    def test_simple(self) -> None:
        line = 'hello\n'
        expected = [
            _PrettyToken(_PrettyTokenType.BODY, 'hello'),
            _PrettyToken(_PrettyTokenType.NEWLINE, '\n'),
        ]

        actual = _tokenize_line(line=line)
        self.assertEqual(actual, expected)

    def test_crlf(self) -> None:
        line = 'hello\r\n'
        expected = [
            _PrettyToken(_PrettyTokenType.BODY, 'hello'),
            _PrettyToken(_PrettyTokenType.NEWLINE, '\r\n'),
        ]

        actual = _tokenize_line(line=line)
        self.assertEqual(actual, expected)

    def test_with_whitespace(self) -> None:
        line = 'hello  \t\tworld\n'
        expected = [
            _PrettyToken(_PrettyTokenType.BODY, 'hello'),
            _PrettyToken(_PrettyTokenType.WHITESPACE, '  \t\t'),
            _PrettyToken(_PrettyTokenType.BODY, 'world'),
            _PrettyToken(_PrettyTokenType.NEWLINE, '\n'),
        ]

        actual = _tokenize_line(line=line)
        self.assertEqual(actual, expected)

    def test_without_newline(self) -> None:
        line = 'hello'
        expected = [
            _PrettyToken(_PrettyTokenType.BODY, 'hello'),
        ]

        actual = _tokenize_line(line=line)
        self.assertEqual(actual, expected)

    def test_trailing_whitespace(self) -> None:
        line = 'hello    \n'
        expected = [
            _PrettyToken(_PrettyTokenType.BODY, 'hello'),
            _PrettyToken(_PrettyTokenType.WHITESPACE, '    '),
            _PrettyToken(_PrettyTokenType.HINT, '(trailing whitespace)'),
            _PrettyToken(_PrettyTokenType.NEWLINE, '\n'),
        ]

        actual = _tokenize_line(line=line)
        self.assertEqual(actual, expected)

    def test_only_newline(self) -> None:
        line = '\n'
        expected = [
            _PrettyToken(_PrettyTokenType.NEWLINE, '\n'),
        ]

        actual = _tokenize_line(line=line)
        self.assertEqual(actual, expected)

    def test_empty_string(self) -> None:
        line = ''
        expected: List[_PrettyToken] = []

        actual = _tokenize_line(line=line)
        self.assertEqual(actual, expected)


class TokenizeLargeFileContentTest(unittest.TestCase):
    def test_small(self) -> None:
        content = b'hello\nworld\n'
        limit = 40
        head = 20
        tail = 10
        char_in_line = 40
        expected = [
            _PrettyToken(_PrettyTokenType.BODY, 'hello'),
            _PrettyToken(_PrettyTokenType.NEWLINE, '\n'),
            _PrettyToken(_PrettyTokenType.BODY, 'world'),
            _PrettyToken(_PrettyTokenType.NEWLINE, '\n'),
        ]

        actual = _tokenize_large_file_content(content=content, limit=limit, head=head, tail=tail, char_in_line=char_in_line)
        self.assertEqual(actual, expected)

    def test_too_many_chars(self) -> None:
        content_chars = 100000
        content = b'hello' * (content_chars // len(b'hello'))
        limit = 40
        head = 20
        tail = 10
        char_in_line = 40
        expected = [
            _PrettyToken(_PrettyTokenType.BODY, 'hello' * (head * char_in_line // len('hello'))),
            _PrettyToken(_PrettyTokenType.HINT, '... ({} chars) ...'.format(content_chars - head * char_in_line - tail * char_in_line)),
            _PrettyToken(_PrettyTokenType.BODY, 'hello' * (tail * char_in_line // len('hello'))),
            _PrettyToken(_PrettyTokenType.HINT, '(no trailing newline)'),
        ]

        actual = _tokenize_large_file_content(content=content, limit=limit, head=head, tail=tail, char_in_line=char_in_line)
        self.assertEqual(actual, expected)

    def test_too_many_lines(self) -> None:
        content_lines = 100
        content = b'hello\n' * content_lines
        limit = 40
        head = 20
        tail = 10
        char_in_line = 40
        expected = []
        for _ in range(head):
            expected += [
                _PrettyToken(_PrettyTokenType.BODY, 'hello'),
                _PrettyToken(_PrettyTokenType.NEWLINE, '\n'),
            ]
        expected += [
            _PrettyToken(_PrettyTokenType.HINT, '... ({} lines) ...\n'.format(content_lines - head - tail)),
        ]
        for _ in range(tail):
            expected += [
                _PrettyToken(_PrettyTokenType.BODY, 'hello'),
                _PrettyToken(_PrettyTokenType.NEWLINE, '\n'),
            ]

        actual = _tokenize_large_file_content(content=content, limit=limit, head=head, tail=tail, char_in_line=char_in_line)
        self.assertEqual(actual, expected)

    def test_empty(self) -> None:
        content = b''
        limit = 40
        head = 20
        tail = 10
        char_in_line = 40
        expected = [
            _PrettyToken(_PrettyTokenType.HINT, '(empty)'),
        ]

        actual = _tokenize_large_file_content(content=content, limit=limit, head=head, tail=tail, char_in_line=char_in_line)
        self.assertEqual(actual, expected)

    def test_only_newlines(self) -> None:
        content = b'\r\n\n'
        limit = 40
        head = 20
        tail = 10
        char_in_line = 40
        expected = [
            _PrettyToken(_PrettyTokenType.NEWLINE, '\r\n'),
            _PrettyToken(_PrettyTokenType.NEWLINE, '\n'),
            _PrettyToken(_PrettyTokenType.HINT, '(only newline)'),
        ]

        actual = _tokenize_large_file_content(content=content, limit=limit, head=head, tail=tail, char_in_line=char_in_line)
        self.assertEqual(actual, expected)


class TokenizeFileContentWithoutSnippingTest(unittest.TestCase):
    def test_small(self) -> None:
        content = b'hello\nworld\n'
        expected = [
            _PrettyToken(_PrettyTokenType.BODY, 'hello'),
            _PrettyToken(_PrettyTokenType.NEWLINE, '\n'),
            _PrettyToken(_PrettyTokenType.BODY, 'world'),
            _PrettyToken(_PrettyTokenType.NEWLINE, '\n'),
        ]

        actual = _tokenize_file_content_without_snipping(content=content)
        self.assertEqual(actual, expected)

    def test_empty(self) -> None:
        content = b''
        expected = [
            _PrettyToken(_PrettyTokenType.HINT, '(empty)'),
        ]

        actual = _tokenize_file_content_without_snipping(content=content)
        self.assertEqual(actual, expected)

    def test_only_newlines(self) -> None:
        content = b'\r\n\n'
        expected = [
            _PrettyToken(_PrettyTokenType.NEWLINE, '\r\n'),
            _PrettyToken(_PrettyTokenType.NEWLINE, '\n'),
            _PrettyToken(_PrettyTokenType.HINT, '(only newline)'),
        ]

        actual = _tokenize_file_content_without_snipping(content=content)
        self.assertEqual(actual, expected)


class RenderTokensTest(unittest.TestCase):
    def test_simple(self) -> None:
        tokens = [
            _PrettyToken(_PrettyTokenType.BODY, 'hello'),
            _PrettyToken(_PrettyTokenType.NEWLINE, '\n'),
            _PrettyToken(_PrettyTokenType.BODY, 'world'),
            _PrettyToken(_PrettyTokenType.NEWLINE, '\n'),
        ]
        expected = ''.join([
            '<bold>hello</bold>',
            '<dim>\n</dim>',
            '<bold>world</bold>',
            '<dim>\n</dim>',
        ])

        font_dim = lambda s: '<dim>' + s + '</dim>'
        font_bold = lambda s: '<bold>' + s + '</bold>'
        actual = _render_tokens(tokens=tokens, font_bold=font_bold, font_dim=font_dim)
        self.assertEqual(actual, expected)

    def test_complicated(self) -> None:
        tokens = [
            _PrettyToken(_PrettyTokenType.BODY, 'hello world'),
            _PrettyToken(_PrettyTokenType.WHITESPACE, ' \t'),
            _PrettyToken(_PrettyTokenType.HINT, 'this is a hint message'),
            _PrettyToken(_PrettyTokenType.NEWLINE, '\r\n'),
        ]
        expected = ''.join([
            '<bold>hello world</bold>',
            '<dim>_\\t</dim>',
            '<dim>this is a hint message</dim>',
            '<dim>\\r\n</dim>',
        ])

        font_dim = lambda s: '<dim>' + s + '</dim>'
        font_bold = lambda s: '<bold>' + s + '</bold>'
        actual = _render_tokens(tokens=tokens, font_bold=font_bold, font_dim=font_dim)
        self.assertEqual(actual, expected)
