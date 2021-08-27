"""This module has unit tests for onlinejudge_command.pretty_printers module.
"""

import textwrap
import unittest
from typing import *

from onlinejudge_command.output_comparators import CompareMode
from onlinejudge_command.pretty_printers import _LineDiffOp, _make_diff_between_file_and_file, _PrettyToken, _PrettyTokenType, _render_tokens, _tokenize_file_content_without_snipping, _tokenize_large_file_content, _tokenize_line, _tokenize_pretty_diff


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


class MakeDiffBetweenFileAndFileTest(unittest.TestCase):
    def test_word_by_word(self) -> None:
        a = ''.join([
            '1 2 3\n',
            '4 -1\n',
            '6\n',
        ])
        b = ''.join([
            '1 2 3\n',
            '4 5\n',
            '6\n',
        ])
        compare_mode = CompareMode.CRLF_INSENSITIVE_EXACT_MATCH
        expected = [
            _LineDiffOp(lineno=1, left=[
                _PrettyToken(_PrettyTokenType.BODY, '4'),
                _PrettyToken(_PrettyTokenType.WHITESPACE, ' '),
                _PrettyToken(_PrettyTokenType.BODY_HIGHLIGHT, '-1'),
                _PrettyToken(_PrettyTokenType.NEWLINE, '\n'),
            ], right=[
                _PrettyToken(_PrettyTokenType.BODY, '4'),
                _PrettyToken(_PrettyTokenType.WHITESPACE, ' '),
                _PrettyToken(_PrettyTokenType.BODY_HIGHLIGHT, '5'),
                _PrettyToken(_PrettyTokenType.NEWLINE, '\n'),
            ]),
        ]

        actual = _make_diff_between_file_and_file(a, b, compare_mode=compare_mode)
        self.assertEqual(actual, expected)

    def test_line_difflib(self) -> None:
        a = ''.join([
            '1 3\n',
            'wow\n',
            'he llo word\n',
        ])
        b = ''.join([
            '1 2 3\n',
            'wow\n',
            'hello world\n',
        ])
        compare_mode = CompareMode.CRLF_INSENSITIVE_EXACT_MATCH
        expected = [
            _LineDiffOp(lineno=0, left=[
                _PrettyToken(type=_PrettyTokenType.BODY, value='1 3'),
                _PrettyToken(type=_PrettyTokenType.NEWLINE, value='\n'),
            ], right=[
                _PrettyToken(type=_PrettyTokenType.BODY, value='1 '),
                _PrettyToken(type=_PrettyTokenType.BODY_HIGHLIGHT, value='2 '),
                _PrettyToken(type=_PrettyTokenType.BODY, value='3'),
                _PrettyToken(type=_PrettyTokenType.NEWLINE, value='\n'),
            ]),
            _LineDiffOp(lineno=2, left=[
                _PrettyToken(type=_PrettyTokenType.BODY, value='he'),
                _PrettyToken(type=_PrettyTokenType.BODY_HIGHLIGHT, value=' '),
                _PrettyToken(type=_PrettyTokenType.BODY, value='llo word'),
                _PrettyToken(type=_PrettyTokenType.NEWLINE, value='\n'),
            ], right=[
                _PrettyToken(type=_PrettyTokenType.BODY, value='hello wor'),
                _PrettyToken(type=_PrettyTokenType.BODY_HIGHLIGHT, value='l'),
                _PrettyToken(type=_PrettyTokenType.BODY, value='d'),
                _PrettyToken(type=_PrettyTokenType.NEWLINE, value='\n'),
            ]),
        ]

        actual = _make_diff_between_file_and_file(a, b, compare_mode=compare_mode)
        self.assertEqual(actual, expected)

    def test_file_difflib(self) -> None:
        a = ''.join([
            'foo\n',
            'baz\n',
            'hello\n',
            'world\n',
            'hey\n',
            'wow\n',
        ])
        b = ''.join([
            'foo\n',
            'bar\n',
            'baz\n',
            'hello\n',
            'world\n',
            'wow\n',
            'wow\n',
        ])
        compare_mode = CompareMode.CRLF_INSENSITIVE_EXACT_MATCH
        expected = [
            _LineDiffOp(lineno=1, left=None, right=[
                _PrettyToken(type=_PrettyTokenType.BODY_HIGHLIGHT, value='bar'),
                _PrettyToken(type=_PrettyTokenType.NEWLINE, value='\n'),
            ]),
            _LineDiffOp(lineno=4, left=[
                _PrettyToken(type=_PrettyTokenType.BODY_HIGHLIGHT, value='hey'),
                _PrettyToken(type=_PrettyTokenType.NEWLINE, value='\n'),
            ], right=None),
            _LineDiffOp(lineno=6, left=None, right=[
                _PrettyToken(type=_PrettyTokenType.BODY_HIGHLIGHT, value='wow'),
                _PrettyToken(type=_PrettyTokenType.NEWLINE, value='\n'),
            ]),
        ]

        actual = _make_diff_between_file_and_file(a, b, compare_mode=compare_mode)
        self.assertEqual(actual, expected)


class MakePrettyDiffTest(unittest.TestCase):
    def test_word_by_word(self) -> None:
        a = ''.join([
            '1 2 3\n',
            '4 -1\n',
            '6\n',
        ])
        b = ''.join([
            '1 2 3\n',
            '4 5\n',
            '6\n',
        ])
        compare_mode = CompareMode.CRLF_INSENSITIVE_EXACT_MATCH
        char_in_line = 40
        limit = 40
        expected = textwrap.dedent("""\
            output:             expected:<dim>
            </dim><blue>1</blue>| <bold>1</bold><dim>_</dim><bold>2</bold><dim>_</dim><bold>3</bold><dim></dim>            <blue>1</blue>| <bold>1</bold><dim>_</dim><bold>2</bold><dim>_</dim><bold>3</bold><dim>
            </dim><blue>2</blue>| <bold>4</bold><dim>_</dim><red>-1</red><dim></dim>             <blue>2</blue>| <bold>4</bold><dim>_</dim><red>5</red><dim>
            </dim><blue>3</blue>| <bold>6</bold><dim></dim>                <blue>3</blue>| <bold>6</bold><dim>
            </dim>""")

        font_dim = lambda s: '<dim>' + s + '</dim>'
        font_bold = lambda s: '<bold>' + s + '</bold>'
        font_red = lambda s: '<red>' + s + '</red>'
        font_blue = lambda s: '<blue>' + s + '</blue>'
        tokens = _tokenize_pretty_diff(a, expected=b, compare_mode=compare_mode, char_in_line=char_in_line, limit=limit)
        actual = _render_tokens(tokens=tokens, font_dim=font_dim, font_bold=font_bold, font_red=font_red, font_blue=font_blue)
        self.assertEqual(actual, expected)

    def test_line_difflib(self) -> None:
        a = ''.join([
            '1 3\n',
            'wow\n',
            'he llo word\n',
        ])
        b = ''.join([
            '1 2 3\n',
            'wow\n',
            'hello world\n',
        ])
        compare_mode = CompareMode.CRLF_INSENSITIVE_EXACT_MATCH
        char_in_line = 40
        limit = 40
        expected = textwrap.dedent("""\
            output:             expected:<dim>
            </dim><blue>1</blue>| <bold>1 3</bold><dim></dim>              <blue>1</blue>| <bold>1 </bold><red>2 </red><bold>3</bold><dim>
            </dim><blue>2</blue>| <bold>wow</bold><dim></dim>              <blue>2</blue>| <bold>wow</bold><dim>
            </dim><blue>3</blue>| <bold>he</bold><red> </red><bold>llo word</bold><dim></dim>      <blue>3</blue>| <bold>hello wor</bold><red>l</red><bold>d</bold><dim>
            </dim>""")

        font_dim = lambda s: '<dim>' + s + '</dim>'
        font_bold = lambda s: '<bold>' + s + '</bold>'
        font_red = lambda s: '<red>' + s + '</red>'
        font_blue = lambda s: '<blue>' + s + '</blue>'
        tokens = _tokenize_pretty_diff(a, expected=b, compare_mode=compare_mode, char_in_line=char_in_line, limit=limit)
        actual = _render_tokens(tokens=tokens, font_dim=font_dim, font_bold=font_bold, font_red=font_red, font_blue=font_blue)
        self.assertEqual(actual, expected)

    def test_file_difflib(self) -> None:
        a = ''.join([
            'foo\n',
            'baz\n',
            'hello\n',
            'world\n',
            'hey\n',
            'wow\n',
        ])
        b = ''.join([
            'foo\n',
            'bar\n',
            'baz\n',
            'hello\n',
            'world\n',
            'wow\n',
            'wow\n',
        ])
        compare_mode = CompareMode.CRLF_INSENSITIVE_EXACT_MATCH
        char_in_line = 40
        limit = 40
        expected = textwrap.dedent("""\
            output:             expected:<dim>
            </dim><blue>1</blue>| <bold>foo</bold><dim></dim>              <blue>1</blue>| <bold>foo</bold><dim>
            </dim>                    <blue>2</blue>| <red>bar</red><dim>
            </dim><blue>2</blue>| <bold>baz</bold><dim></dim>              <blue>3</blue>| <bold>baz</bold><dim>
            </dim><blue>3</blue>| <bold>hello</bold><dim></dim>            <blue>4</blue>| <bold>hello</bold><dim>
            </dim><blue>4</blue>| <bold>world</bold><dim></dim>            <blue>5</blue>| <bold>world</bold><dim>
            </dim><blue>5</blue>| <red>hey</red><dim></dim>              
            <blue>6</blue>| <bold>wow</bold><dim></dim>              <blue>6</blue>| <bold>wow</bold><dim>
            </dim>                    <blue>7</blue>| <red>wow</red><dim>
            </dim>""")

        font_dim = lambda s: '<dim>' + s + '</dim>'
        font_bold = lambda s: '<bold>' + s + '</bold>'
        font_red = lambda s: '<red>' + s + '</red>'
        font_blue = lambda s: '<blue>' + s + '</blue>'
        tokens = _tokenize_pretty_diff(a, expected=b, compare_mode=compare_mode, char_in_line=char_in_line, limit=limit)
        actual = _render_tokens(tokens=tokens, font_dim=font_dim, font_bold=font_bold, font_red=font_red, font_blue=font_blue)
        self.assertEqual(actual, expected)
