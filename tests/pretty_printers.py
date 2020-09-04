"""This module has unit tests for onlinejudge_command.pretty_printers module.
"""

import unittest

from onlinejudge_command.pretty_printers import _PrettyToken, _PrettyTokenType, _render_tokens_for_large_file_content, _tokenize_large_file_content


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


class RenderTokensForLargeFileContentTest(unittest.TestCase):
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
        actual = _render_tokens_for_large_file_content(tokens=tokens, font_bold=font_bold, font_dim=font_dim)
        self.assertEqual(actual, expected)

    def test_complicated(self) -> None:
        tokens = [
            _PrettyToken(_PrettyTokenType.BODY, 'hello world'),
            _PrettyToken(_PrettyTokenType.WHITESPACE, ' \t'),
            _PrettyToken(_PrettyTokenType.NEWLINE, '\r\n'),
        ]
        expected = ''.join([
            '<bold>hello world</bold>',
            '<dim>_\\t</dim>',
            '<dim>\\r\n</dim>',
        ])

        font_dim = lambda s: '<dim>' + s + '</dim>'
        font_bold = lambda s: '<bold>' + s + '</bold>'
        actual = _render_tokens_for_large_file_content(tokens=tokens, font_bold=font_bold, font_dim=font_dim)
        self.assertEqual(actual, expected)
