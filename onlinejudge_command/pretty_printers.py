import difflib
import enum
import shutil
from logging import getLogger
from typing import *

import colorama

from onlinejudge_command.output_comparators import CompareMode, check_lines_match

logger = getLogger(__name__)


class _PrettyTokenType(enum.Enum):
    BODY = 'BODY'
    BODY_HIGHLIGHT_LEFT = 'BODY_HIGHLIGHT_LEFT'
    BODY_HIGHLIGHT_RIGHT = 'BODY_HIGHLIGHT_RIGHT'
    WHITESPACE = 'WHITESPACE'
    NEWLINE = 'NEWLINE'
    HINT = 'HINT'
    LINENO = 'LINENO'
    OTHERS = 'OTHERS'


class _PrettyToken(NamedTuple):
    type: _PrettyTokenType
    value: str


def _optimize_tokens(tokens: List[_PrettyToken]) -> List[_PrettyToken]:
    optimized: List[_PrettyToken] = []
    for token in tokens:
        if optimized and optimized[-1].type == token.type:
            optimized[-1] = _PrettyToken(token.type, optimized[-1].value + token.value)
        else:
            optimized.append(token)
    return optimized


def _tokenize_str(s: str) -> List[_PrettyToken]:
    tokens = []
    l = 0
    while l < len(s):
        r = l + 1
        while r < len(s) and (s[l] in ' \t') == (s[r] in ' \t'):
            r += 1
        if s[l] in ' \t':
            typ = _PrettyTokenType.WHITESPACE
        else:
            typ = _PrettyTokenType.BODY
        tokens.append(_PrettyToken(typ, s[l:r]))
        l = r
    return tokens


def _tokenize_line(line: str) -> List[_PrettyToken]:
    body = line.rstrip()
    newline = line[len(body):]
    tokens = []

    # add the body of line
    if body:
        tokens += _tokenize_str(body)

    # add newlines
    if newline:
        if newline in ('\n', '\r\n'):
            tokens.append(_PrettyToken(_PrettyTokenType.NEWLINE, newline))
        else:
            whitespace = newline.rstrip('\n')
            newline = newline[len(whitespace):]
            if whitespace:
                tokens.append(_PrettyToken(_PrettyTokenType.WHITESPACE, whitespace))
            tokens.append(_PrettyToken(_PrettyTokenType.HINT, '(trailing whitespace)'))
            if newline:
                tokens.append(_PrettyToken(_PrettyTokenType.NEWLINE, newline))

    return tokens


def _decode_with_recovery(content: bytes) -> Tuple[List[_PrettyToken], str]:
    tokens = []
    try:
        text = content.decode()
    except UnicodeDecodeError as e:
        tokens.append(_PrettyToken(_PrettyTokenType.HINT, str(e)))
        text = content.decode(errors='replace')
    return tokens, text


def _warn_if_empty(tokens: List[_PrettyToken]) -> List[_PrettyToken]:
    if not tokens:
        return [_PrettyToken(_PrettyTokenType.HINT, '(empty)')]
    if tokens[-1][0] == _PrettyTokenType.BODY:
        tokens.append(_PrettyToken(_PrettyTokenType.HINT, '(no trailing newline)'))
    if all(token.type == _PrettyTokenType.NEWLINE for token in tokens):
        tokens.append(_PrettyToken(_PrettyTokenType.HINT, '(only newline)'))
    return tokens


def _tokenize_large_file_content(*, content: bytes, limit: int, head: int, tail: int, char_in_line: int) -> List[_PrettyToken]:
    """`_tokenize_large_file_content` constructs the intermediate representations. They have no color infomation.
    """

    assert head + tail < limit

    def candidate_do_nothing(text: str) -> List[_PrettyToken]:
        tokens = []
        for line in text.splitlines(keepends=True):
            tokens += _tokenize_line(line)
        return tokens

    def candidate_line_based(text: str) -> List[_PrettyToken]:
        lines = text.splitlines(keepends=True)
        if len(lines) < limit:
            return candidate_do_nothing(text)

        tokens = []
        for line in lines[:head]:
            tokens += _tokenize_line(line)
        tokens.append(_PrettyToken(_PrettyTokenType.HINT, '... ({} lines) ...\n'.format(len(lines[head:-tail]))))
        for line in lines[-tail:]:
            tokens += _tokenize_line(line)
        return tokens

    def candidate_char_based(text: str) -> List[_PrettyToken]:
        if len(text) < char_in_line * limit:
            return candidate_do_nothing(text)

        l = len(text[:char_in_line * head].rstrip())
        r = len(text) - char_in_line * tail
        tokens = []
        for line in text[:l].splitlines(keepends=True):
            tokens += _tokenize_line(line)
        tokens.append(_PrettyToken(_PrettyTokenType.HINT, '... ({} chars) ...'.format(r - l)))
        for line in text[r:].splitlines(keepends=True):
            tokens += _tokenize_line(line)
        return tokens

    def count_size(tokens: Iterable[_PrettyToken]) -> int:
        size = 0
        for _, s in tokens:
            size += len(s)
        return size

    # Choose the shortest one from the three candidates.
    tokens, text = _decode_with_recovery(content)
    if text:
        candidates: List[List[_PrettyToken]] = [
            candidate_do_nothing(text),
            candidate_line_based(text),
            candidate_char_based(text),
        ]
        tokens.extend(min(candidates, key=count_size))
    tokens = _warn_if_empty(tokens)
    return tokens


def _replace_whitespace(s: str) -> str:
    return s.replace(' ', '_').replace('\t', '\\t').replace('\r', '\\r')


def _render_tokens(
    *,
    tokens: List[_PrettyToken],
    font_bold: Optional[Callable[[str], str]] = None,
    font_dim: Optional[Callable[[str], str]] = None,
    font_red: Optional[Callable[[str], str]] = None,
    font_blue: Optional[Callable[[str], str]] = None,
    font_normal: Optional[Callable[[str], str]] = None,
) -> str:
    """`_tokenize_large_file_content` generate the result string. It is colored.
    """

    if font_bold is None:
        font_bold = lambda s: colorama.Style.BRIGHT + s + colorama.Style.RESET_ALL
    if font_dim is None:
        font_dim = lambda s: colorama.Style.DIM + s + colorama.Style.RESET_ALL
    if font_red is None:
        font_red = lambda s: colorama.Fore.RED + s + colorama.Style.RESET_ALL
    if font_blue is None:
        font_blue = lambda s: colorama.Fore.CYAN + s + colorama.Style.RESET_ALL
    if font_normal is None:
        font_normal = lambda s: s

    result = []
    for key, value in tokens:
        if key == _PrettyTokenType.BODY:
            value = font_bold(value)
        elif key == _PrettyTokenType.BODY_HIGHLIGHT_LEFT:
            value = font_red(value)
        elif key == _PrettyTokenType.BODY_HIGHLIGHT_RIGHT:
            value = font_red(value)
        elif key == _PrettyTokenType.WHITESPACE:
            value = font_dim(_replace_whitespace(value))
        elif key == _PrettyTokenType.NEWLINE:
            value = font_dim(_replace_whitespace(value))
        elif key == _PrettyTokenType.HINT:
            value = font_dim(value)
        elif key == _PrettyTokenType.LINENO:
            value = font_blue(value)
        elif key == _PrettyTokenType.OTHERS:
            value = font_normal(value)
        else:
            assert False
        result.append(value)
    return ''.join(result)


def _get_terminal_size() -> int:
    char_in_line, _ = shutil.get_terminal_size()
    return max(char_in_line, 40)  # shutil.get_terminal_size() may return too small values (e.g. (0, 0) on Circle CI) successfully (i.e. fallback is not used). see https://github.com/kmyk/online-judge-tools/pull/611


def make_pretty_large_file_content(content: bytes, limit: int, head: int, tail: int) -> str:
    char_in_line = _get_terminal_size()
    tokens = _tokenize_large_file_content(content=content, limit=limit, head=head, tail=tail, char_in_line=char_in_line)
    return _render_tokens(tokens=tokens)


def _tokenize_file_content_without_snipping(content: bytes) -> List[_PrettyToken]:
    tokens, text = _decode_with_recovery(content)
    for line in text.splitlines(keepends=True):
        tokens += _tokenize_line(line)
    tokens = _warn_if_empty(tokens)
    return tokens


def make_pretty_all(content: bytes) -> str:
    tokens = _tokenize_file_content_without_snipping(content=content)
    return _render_tokens(tokens=tokens)


def _skip_whitespaces(i: int, s: str) -> Tuple[int, List[_PrettyToken]]:
    tokens = []
    while i < len(s) and s[i] in ' \t\r\n':
        if s[i] in ' \t':
            typ = _PrettyTokenType.WHITESPACE
        else:
            typ = _PrettyTokenType.NEWLINE
        tokens.append(_PrettyToken(typ, s[i]))
        i += 1
    return i, _optimize_tokens(tokens)


# This function assumes that the two strings have the same number of words.
def _make_diff_between_line_and_line_by_comparing_word_by_word(a: str, b: str) -> Tuple[List[_PrettyToken], List[_PrettyToken]]:
    assert len(a.strip().split()) == len(b.strip().split())

    tokens_a = []
    tokens_b = []
    l_a = 0
    l_b = 0

    def skip_whitespaces() -> None:
        nonlocal tokens_a
        nonlocal tokens_b
        nonlocal l_a
        nonlocal l_b
        l_a, tokens = _skip_whitespaces(l_a, a)
        tokens_a += tokens
        l_b, tokens = _skip_whitespaces(l_b, b)
        tokens_b += tokens

    skip_whitespaces()

    while l_a < len(a) and l_b < len(b):
        # get next words
        r_a = l_a + 1
        r_b = l_b + 1
        while r_a < len(a) and a[r_a] not in ' \t\r\n':
            r_a += 1
        while r_b < len(b) and b[r_b] not in ' \t\r\n':
            r_b += 1
        word_a = a[l_a:r_a]
        word_b = b[l_b:r_b]

        # compare two words
        if word_a == word_b:
            tokens_a.append(_PrettyToken(_PrettyTokenType.BODY, word_a))
            tokens_b.append(_PrettyToken(_PrettyTokenType.BODY, word_b))
        else:
            tokens_a.append(_PrettyToken(_PrettyTokenType.BODY_HIGHLIGHT_LEFT, word_a))
            tokens_b.append(_PrettyToken(_PrettyTokenType.BODY_HIGHLIGHT_RIGHT, word_b))

        l_a = r_a
        l_b = r_b
        skip_whitespaces()

    assert l_a == len(a) and l_b == len(b)  # The two strings have the same number of words, so this must be true.
    return tokens_a, tokens_b


def _tokenize_str_with_highlight(s: str, *, is_right: bool) -> List[_PrettyToken]:
    tokens: List[_PrettyToken] = []
    for token in _tokenize_str(s):
        if token.type == _PrettyTokenType.BODY:
            typ = _PrettyTokenType.BODY_HIGHLIGHT_RIGHT if is_right else _PrettyTokenType.BODY_HIGHLIGHT_LEFT
            tokens.append(_PrettyToken(typ, token.value))
        else:
            tokens.append(token)
    return tokens


def _make_diff_between_line_and_line_by_difflib(a: str, b: str) -> Tuple[List[_PrettyToken], List[_PrettyToken]]:
    tokens_a = []
    tokens_b = []

    # https://docs.python.org/ja/3/library/difflib.html#difflib.SequenceMatcher.get_opcodes
    matcher: difflib.SequenceMatcher = difflib.SequenceMatcher()
    matcher.set_seqs(a.rstrip('\n'), b.rstrip('\n'))
    for (tag, l_a, r_a, l_b, r_b) in matcher.get_opcodes():
        if tag == 'replace':
            tokens_a.extend(_tokenize_str_with_highlight(a[l_a:r_a], is_right=False))
            tokens_b.extend(_tokenize_str_with_highlight(b[l_b:r_b], is_right=True))
        elif tag == 'delete':
            assert l_b == r_b
            tokens_a.extend(_tokenize_str_with_highlight(a[l_a:r_a], is_right=False))
        elif tag == 'insert':
            assert l_a == r_a
            tokens_b.extend(_tokenize_str_with_highlight(b[l_b:r_b], is_right=True))
        elif tag == 'equal':
            tokens_a.extend(_tokenize_str(a[l_a:r_a]))
            tokens_b.extend(_tokenize_str(b[l_b:r_b]))
        else:
            assert False

    if len(a.rstrip('\n')) < len(a):
        tokens_a.append(_PrettyToken(_PrettyTokenType.NEWLINE, a[len(a.rstrip('\n')):]))
    if len(b.rstrip('\n')) < len(b):
        tokens_b.append(_PrettyToken(_PrettyTokenType.NEWLINE, b[len(b.rstrip('\n')):]))
    tokens_a = _optimize_tokens(tokens_a)
    tokens_b = _optimize_tokens(tokens_b)
    return tokens_a, tokens_b


def _make_diff_between_line_and_line(a: str, b: str) -> Tuple[List[_PrettyToken], List[_PrettyToken]]:
    if len(a.strip().split()) == len(b.strip().split()):
        return _make_diff_between_line_and_line_by_comparing_word_by_word(a, b)
    else:
        return _make_diff_between_line_and_line_by_difflib(a, b)


class _LineDiffOp(NamedTuple):
    lineno: int  # 0-based. This may be an index of the left side, the right side or the both sides.
    left: Optional[List[_PrettyToken]]
    right: Optional[List[_PrettyToken]]


# This function assumes that the two strings have the same number of lines.
def _make_diff_between_file_and_file_by_comparing_line_by_line(a: str, b: str, *, compare_mode: CompareMode) -> List[_LineDiffOp]:
    assert compare_mode != CompareMode.IGNORE_SPACES_AND_NEWLINES
    assert len(a.rstrip().splitlines()) == len(b.rstrip().splitlines())

    ops = []
    lines_a = a.splitlines(keepends=True)
    lines_b = b.splitlines(keepends=True)
    i = 0

    # compare line by line
    while i < min(len(lines_a), len(lines_b)):
        if not check_lines_match(lines_a[i], lines_b[i], compare_mode=compare_mode):
            tokens_a, tokens_b = _make_diff_between_line_and_line(lines_a[i], lines_b[i])
            ops.append(_LineDiffOp(i, tokens_a, tokens_b))
        i += 1

    # put diff of trailing newlines
    if compare_mode in (CompareMode.EXACT_MATCH, CompareMode.CRLF_INSENSITIVE_EXACT_MATCH):
        while i < len(lines_a):
            tokens_a = _tokenize_line(lines_a[i])
            ops.append(_LineDiffOp(i, tokens_a, None))
            i += 1
        while i < len(lines_b):
            tokens_b = _tokenize_line(lines_b[i])
            ops.append(_LineDiffOp(i, None, tokens_b))
            i += 1

    return ops


def _tokenize_line_with_highlight(line: str, *, is_right: bool) -> List[_PrettyToken]:
    tokens: List[_PrettyToken] = []
    for token in _tokenize_line(line):
        if token.type == _PrettyTokenType.BODY:
            typ = _PrettyTokenType.BODY_HIGHLIGHT_RIGHT if is_right else _PrettyTokenType.BODY_HIGHLIGHT_LEFT
            tokens.append(_PrettyToken(typ, token.value))
        else:
            tokens.append(token)
    return tokens


# This function works as --compare-mode=exact-match.
def _make_diff_between_file_and_file_by_difflib(a: str, b: str) -> List[_LineDiffOp]:
    lines_a = a.splitlines(keepends=True)
    lines_b = b.splitlines(keepends=True)
    ops = []

    # https://docs.python.org/ja/3/library/difflib.html#difflib.SequenceMatcher.get_opcodes
    matcher: difflib.SequenceMatcher = difflib.SequenceMatcher()
    matcher.set_seqs(lines_a, lines_b)
    for (tag, l_a, r_a, l_b, r_b) in matcher.get_opcodes():
        if tag == 'replace':
            while l_a < r_a and l_a < l_b:
                tokens = _tokenize_line_with_highlight(lines_a[l_a], is_right=False)
                ops.append(_LineDiffOp(l_a, tokens, None))
                l_a += 1
            while l_b < r_b and l_b < l_a:
                tokens = _tokenize_line_with_highlight(lines_b[l_b], is_right=True)
                ops.append(_LineDiffOp(l_b, None, tokens))
                l_b += 1
            while l_a < r_a and l_b < r_b:
                assert l_a == l_b
                tokens_a = _tokenize_line_with_highlight(lines_a[l_a], is_right=False)
                tokens_b = _tokenize_line_with_highlight(lines_b[l_b], is_right=True)
                ops.append(_LineDiffOp(l_a, tokens_a, tokens_b))
                l_a += 1
                l_b += 1
            while l_a < r_a:
                tokens = _tokenize_line_with_highlight(lines_a[l_a], is_right=False)
                ops.append(_LineDiffOp(l_a, tokens, None))
                l_a += 1
            while l_b < r_b:
                tokens = _tokenize_line_with_highlight(lines_b[l_b], is_right=True)
                ops.append(_LineDiffOp(l_b, None, tokens))
                l_b += 1

        elif tag == 'delete':
            assert l_b == r_b
            for i in range(l_a, r_a):
                tokens = _tokenize_line_with_highlight(lines_a[i], is_right=False)
                ops.append(_LineDiffOp(i, tokens, None))

        elif tag == 'insert':
            assert l_a == r_a
            for i in range(l_b, r_b):
                tokens = _tokenize_line_with_highlight(lines_b[i], is_right=True)
                ops.append(_LineDiffOp(i, None, tokens))

        elif tag == 'equal':
            pass

        else:
            assert False

    return ops


def _make_diff_between_file_and_file(a: str, b: str, *, compare_mode: CompareMode) -> List[_LineDiffOp]:
    assert compare_mode != CompareMode.IGNORE_SPACES_AND_NEWLINES
    if len(a.rstrip().splitlines()) == len(b.rstrip().splitlines()):
        return _make_diff_between_file_and_file_by_comparing_line_by_line(a, b, compare_mode=compare_mode)
    else:
        if compare_mode in (CompareMode.IGNORE_SPACES, CompareMode.IGNORE_SPACES_AND_NEWLINES):
            logger.warning('ignoring --compare-mode=%s and using --compare-mode=%s (default) instead for generating diff...', str(compare_mode), str(CompareMode.CRLF_INSENSITIVE_EXACT_MATCH))
            compare_mode = CompareMode.CRLF_INSENSITIVE_EXACT_MATCH
        if compare_mode == CompareMode.CRLF_INSENSITIVE_EXACT_MATCH:
            if '\r' in a or '\r' in b:
                logger.warning("carriage return '\\r' is removed from diff")
                a = a.replace('\r\n', '\n')
                b = b.replace('\r\n', '\n')
        return _make_diff_between_file_and_file_by_difflib(a, b)


class _MergedDiffOp(NamedTuple):
    left_lineno: Optional[int]  # 0-based
    left: List[_PrettyToken]
    right_lineno: Optional[int]  # 0-based
    right: List[_PrettyToken]
    has_diff: bool


_MergedDiffOpDots = _MergedDiffOp(None, [], None, [], False)  # This represents insertion of "...".


def _reconstruct_entire_diff(a: str, b: str, *, ops: List[_LineDiffOp]) -> List[_MergedDiffOp]:
    lines_a = a.splitlines(keepends=True)
    lines_b = b.splitlines(keepends=True)
    i_a = 0
    i_b = 0
    stk = list(reversed(ops))
    result = []

    while i_a < len(lines_a) and i_b < len(lines_b):
        if stk and stk[-1].left is not None and stk[-1].right is not None and i_a == stk[-1].lineno:
            assert i_b == stk[-1].lineno
            result.append(_MergedDiffOp(i_a, stk[-1].left, i_b, stk[-1].right, True))
            stk.pop()
            i_a += 1
            i_b += 1
        elif stk and stk[-1].left is not None and stk[-1].right is None and i_a == stk[-1].lineno:
            result.append(_MergedDiffOp(i_a, stk[-1].left, None, [], True))
            stk.pop()
            i_a += 1
        elif stk and stk[-1].left is None and stk[-1].right is not None and i_b == stk[-1].lineno:
            result.append(_MergedDiffOp(None, [], i_b, stk[-1].right, True))
            stk.pop()
            i_b += 1
        else:
            tokens_a = _tokenize_line(lines_a[i_a])
            tokens_b = _tokenize_line(lines_b[i_b])
            result.append(_MergedDiffOp(i_a, tokens_a, i_b, tokens_b, False))
            i_a += 1
            i_b += 1
    while stk:
        if stk[-1].left is not None and stk[-1].right is None and i_a == stk[-1].lineno:
            result.append(_MergedDiffOp(i_a, stk[-1].left, None, [], True))
            stk.pop()
            i_a += 1
        elif stk[-1].left is None and stk[-1].right is not None and i_b == stk[-1].lineno:
            result.append(_MergedDiffOp(None, [], i_b, stk[-1].right, True))
            stk.pop()
            i_b += 1
        else:
            assert False
    assert i_a == len(lines_a) and i_b == len(lines_b)

    return result


def _add_lines_around_diff_lines(a: str, b: str, *, ops: List[_LineDiffOp], size: int) -> List[_MergedDiffOp]:
    result: List[_MergedDiffOp] = []
    unused: List[_MergedDiffOp] = []
    use = 0
    for op in _reconstruct_entire_diff(a, b, ops=ops):
        if op.has_diff:
            result += unused[-size:]
            unused = []
            result.append(op)
            use = size
        else:
            if use:
                result.append(op)
                use -= 1
            else:
                unused.append(op)
    return result


def _add_dots_between_gaps(a: str, b: str, *, ops: List[_MergedDiffOp]) -> List[_MergedDiffOp]:
    result: List[_MergedDiffOp] = []

    # body
    for op in ops:
        if result and result[-1].left_lineno is not None and result[-1].right_lineno is not None:
            if op.left_lineno is not None and op.right_lineno is not None:
                if op.left_lineno - result[-1].left_lineno >= 2 and op.right_lineno - result[-1].right_lineno >= 2:
                    result.append(_MergedDiffOpDots)
        result.append(op)

    # header and footer
    lines_a = a.splitlines(keepends=True)
    lines_b = b.splitlines(keepends=True)
    min_left_lineno = len(lines_a)
    max_left_lineno = -1
    min_right_lineno = len(lines_b)
    max_right_lineno = -1
    for op in ops:
        if op.left_lineno is not None:
            min_left_lineno = min(min_left_lineno, op.left_lineno)
            max_left_lineno = op.left_lineno
        if op.right_lineno is not None:
            min_right_lineno = min(min_right_lineno, op.right_lineno)
            max_right_lineno = op.right_lineno
    if min_left_lineno != 0 or min_right_lineno != 0:
        result = [_MergedDiffOpDots] + result
    if max_left_lineno != len(lines_a) - 1 or max_right_lineno != len(lines_b) - 1:
        result += [_MergedDiffOpDots]

    return result


def _len_of_tokens(tokens: List[_PrettyToken]) -> int:
    result = 0
    for token in tokens:
        if token.type in (_PrettyTokenType.WHITESPACE, _PrettyTokenType.NEWLINE):
            result += len(_replace_whitespace(token.value).replace('\n', ''))
        else:
            result += len(token.value)
    return result


def _tokens_from_line_diff_ops(ops: List[_MergedDiffOp], *, char_in_line: int) -> List[_PrettyToken]:
    if not ops:
        return [_PrettyToken(_PrettyTokenType.HINT, '(no diff)')]

    left_width = char_in_line // 2

    # calculate the widths of lineno
    max_left_linno = 0
    max_right_linno = 0
    for op in ops:
        if op.left_lineno is not None:
            max_left_linno = op.left_lineno
        if op.right_lineno is not None:
            max_right_linno = op.right_lineno
    left_lineno_width = len(str(max_left_linno + 1))
    right_lineno_width = len(str(max_right_linno + 1))
    assert left_lineno_width + 2 + 10 <= left_width
    assert right_lineno_width + 2 + 10

    tokens = []
    tokens.append(_PrettyToken(_PrettyTokenType.OTHERS, 'output:'.ljust(left_width) + 'expected:'))
    tokens.append(_PrettyToken(_PrettyTokenType.NEWLINE, '\n'))
    for op in ops:
        if op == _MergedDiffOpDots:
            tokens.append(_PrettyToken(_PrettyTokenType.OTHERS, '...'.ljust(left_width) + '...'))
            tokens.append(_PrettyToken(_PrettyTokenType.NEWLINE, '\n'))
            continue
        left_exists = False
        if op.left_lineno is not None:
            tokens.append(_PrettyToken(_PrettyTokenType.LINENO, str(op.left_lineno + 1).rjust(left_lineno_width)))
            tokens.append(_PrettyToken(_PrettyTokenType.OTHERS, '| '))
            tokens.extend([_PrettyToken(token.type, token.value.replace('\n', '')) for token in op.left])
            padding = left_width - (left_lineno_width + 2 + _len_of_tokens(op.left))
            if padding >= 0:
                tokens.append(_PrettyToken(_PrettyTokenType.OTHERS, ' ' * padding))
                left_exists = True
            else:
                tokens.append(_PrettyToken(_PrettyTokenType.OTHERS, '\n'))
        if op.right_lineno is not None:
            if not left_exists:
                tokens.append(_PrettyToken(_PrettyTokenType.OTHERS, ' ' * left_width))
            tokens.append(_PrettyToken(_PrettyTokenType.LINENO, str(op.right_lineno + 1).rjust(right_lineno_width)))
            tokens.append(_PrettyToken(_PrettyTokenType.OTHERS, '| '))
            tokens.extend(op.right)
        else:
            if left_exists:
                tokens.append(_PrettyToken(_PrettyTokenType.OTHERS, '\n'))
    return tokens


def _summary_token_of_diff_ops(ops: List[_MergedDiffOp]) -> List[_PrettyToken]:
    removed = 0
    added = 0
    for op in ops:
        if op.has_diff:
            if op.left_lineno is not None:
                removed += 1
            if op.right_lineno is not None:
                added += 1
    if not removed and not added:
        return []
    else:
        return [_PrettyToken(_PrettyTokenType.HINT, '(also {} lines are deleted and {} lines are added...)'.format(removed, added))]


def _tokenize_pretty_diff(output: str, *, expected: str, compare_mode: CompareMode, char_in_line: int, limit: int) -> List[_PrettyToken]:
    if compare_mode == CompareMode.IGNORE_SPACES_AND_NEWLINES:
        logger.warning('ignoring --compare-mode=%s and using --compare-mode=%s instead for generating diff...', str(compare_mode), str(CompareMode.IGNORE_SPACES))
        compare_mode = CompareMode.IGNORE_SPACES
    ops = _make_diff_between_file_and_file(output, expected, compare_mode=compare_mode)
    merged_ops = _add_lines_around_diff_lines(output, expected, ops=ops, size=4)
    merged_ops = _add_dots_between_gaps(output, expected, ops=merged_ops)
    tokens = _tokens_from_line_diff_ops(merged_ops[:limit] if limit != -1 else merged_ops, char_in_line=char_in_line)
    if limit != -1:
        tokens += _summary_token_of_diff_ops(merged_ops[limit:])
    return tokens


def make_pretty_diff(output_bytes: bytes, *, expected: str, compare_mode: CompareMode, limit: int) -> str:
    tokens, output = _decode_with_recovery(output_bytes)
    char_in_line = _get_terminal_size()
    tokens += _tokenize_pretty_diff(output, expected=expected, compare_mode=compare_mode, char_in_line=char_in_line, limit=limit)
    return _render_tokens(tokens=tokens)
