import collections
import enum
import itertools
import re
import shutil
from logging import getLogger
from typing import *

import colorama
import diff_match_patch

import onlinejudge_command.utils as utils

logger = getLogger(__name__)


class _PrettyTokenType(enum.Enum):
    BODY = 'BODY'
    WHITESPACE = 'WHITESPACE'
    NEWLINE = 'NEWLINE'
    HINT = 'HINT'


class _PrettyToken(NamedTuple):
    type: _PrettyTokenType
    value: str


def _tokenize_large_file_content(*, content: bytes, limit: int, head: int, tail: int, char_in_line: int) -> List[_PrettyToken]:
    """`_tokenize_large_file_content` constructs the intermediate representations. They have no color infomation.
    """

    assert head + tail < limit

    def from_line(line: str) -> List[_PrettyToken]:
        body = line.rstrip()
        newline = line[len(body):]
        tokens = []
        tokens.append(_PrettyToken(_PrettyTokenType.BODY, body))
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

    def candidate_do_nothing(text: str) -> List[_PrettyToken]:
        tokens = []
        for line in text.splitlines(keepends=True):
            tokens += from_line(line)
        return tokens

    def candidate_line_based(text: str) -> List[_PrettyToken]:
        lines = text.splitlines(keepends=True)
        if len(lines) < limit:
            return candidate_do_nothing(text)

        tokens = []
        for line in lines[:head]:
            tokens += from_line(line)
        tokens.append(_PrettyToken(_PrettyTokenType.HINT, '... ({} lines) ...\n'.format(len(lines[head:-tail]))))
        for line in lines[-tail:]:
            tokens += from_line(line)
        return tokens

    def candidate_char_based(text: str) -> List[_PrettyToken]:
        if len(text) < char_in_line * limit:
            return candidate_do_nothing(text)

        l = len(text[:char_in_line * head].rstrip())
        r = len(text) - char_in_line * tail
        tokens = []
        for line in text[:l].splitlines(keepends=True):
            tokens += from_line(line)
        tokens.append(_PrettyToken(_PrettyTokenType.HINT, '... ({} chars) ...'.format(r - l)))
        for line in text[r:].splitlines(keepends=True):
            tokens += from_line(line)
        return tokens

    def count_size(tokens: Iterable[_PrettyToken]) -> int:
        size = 0
        for _, s in tokens:
            size += len(s)
        return size

    if not content:
        return [_PrettyToken(_PrettyTokenType.HINT, '(empty)')]

    tokens = []
    try:
        text = content.decode()
    except UnicodeDecodeError as e:
        tokens.append(_PrettyToken(_PrettyTokenType.HINT, str(e)))
        text = content.decode(errors='replace')

    candidates: List[List[_PrettyToken]] = [
        candidate_do_nothing(text),
        candidate_line_based(text),
        candidate_char_based(text),
    ]
    tokens.extend(min(candidates, key=count_size))

    assert len(tokens) >= 1
    if tokens[-1][0] == _PrettyTokenType.BODY:
        tokens.append(_PrettyToken(_PrettyTokenType.HINT, '(no trailing newline)'))
    if not text.rstrip('\n'):
        tokens.append(_PrettyToken(_PrettyTokenType.HINT, '(only newline)'))

    return tokens


def _render_tokens_for_large_file_content(*, tokens: List[_PrettyToken], font_bold: Callable[[str], str], font_dim: Callable[[str], str]) -> str:
    """`_tokenize_large_file_content` generate the result string. It is colored.
    """

    result = []
    for key, value in tokens:
        if key == _PrettyTokenType.BODY:
            value = font_bold(value)
        elif key == _PrettyTokenType.WHITESPACE:
            value = font_dim(value.replace(' ', '_').replace('\t', '\\t').replace('\r', '\\r'))
        elif key == _PrettyTokenType.NEWLINE:
            value = font_dim(value.replace('\r', '\\r'))
        elif key == _PrettyTokenType.HINT:
            value = font_dim(value)
        else:
            assert False
        result.append(value)
    return ''.join(result)


def make_pretty_large_file_content(content: bytes, limit: int, head: int, tail: int, bold: bool = False) -> str:
    char_in_line, _ = shutil.get_terminal_size()
    char_in_line = max(char_in_line, 40)  # shutil.get_terminal_size() may return too small values (e.g. (0, 0) on Circle CI) successfully (i.e. fallback is not used). see https://github.com/kmyk/online-judge-tools/pull/611
    tokens = _tokenize_large_file_content(content=content, limit=limit, head=head, tail=tail, char_in_line=char_in_line)

    if bold:
        font_bold = lambda s: colorama.Style.BRIGHT + s + colorama.Style.RESET_ALL
    else:
        font_bold = lambda s: s
    font_dim = lambda s: colorama.Style.DIM + s + colorama.Style.RESET_ALL
    return _render_tokens_for_large_file_content(tokens=tokens, font_bold=font_bold, font_dim=font_dim)


def _space_padding(s: str, max_length: int) -> str:
    return s + " " * max_length


# NOTE: untested
def display_side_by_side_color(answer: str, expected: str) -> None:
    max_chars = shutil.get_terminal_size()[0] // 2 - 2

    logger.info(utils.NO_HEADER + 'output:' + " " * (max_chars - 7) + "|" + "expected:")
    logger.info(utils.NO_HEADER + '%s', "-" * max_chars + "|" + "-" * max_chars)
    for _, diff_found, ans_line, exp_line, ans_chars, _ in _side_by_side_diff(answer, expected):
        if diff_found:
            logger.info(utils.NO_HEADER + '%s', utils.red(_space_padding(ans_line, max_chars - ans_chars)) + "|" + utils.green(exp_line))
        else:
            logger.info(utils.NO_HEADER + '%s', _space_padding(ans_line, max_chars - ans_chars) + "|" + exp_line)


# NOTE: untested
def display_snipped_side_by_side_color(answer: str, expected: str) -> None:
    """
    Display first differ line and its previous 3 lines and its next 3 lines.
    """
    max_chars = shutil.get_terminal_size()[0] // 2 - 2
    deq: Deque[Tuple[Optional[int], bool, str, str, int, int]] = collections.deque(maxlen=7)

    count_from_first_difference = 0
    i = 0
    for flag, diff_found, ans_line, exp_line, ans_chars, exp_chars in _side_by_side_diff(answer, expected):
        if flag:
            i += 1
        if count_from_first_difference > 0:
            count_from_first_difference += 1
        line_num = i if flag else None
        deq.append((line_num, diff_found, ans_line, exp_line, ans_chars, exp_chars))
        if diff_found:
            if count_from_first_difference == 0:
                count_from_first_difference = 1
        if count_from_first_difference == 4:
            break

    max_line_num_digits = max([len(str(entry[0])) for entry in deq if entry[0] is not None])

    logger.info(utils.NO_HEADER + '%s', " " * max_line_num_digits + "|output:" + " " * (max_chars - 7 - max_line_num_digits - 1) + "|" + "expected:")
    logger.info(utils.NO_HEADER + '%s', "-" * max_chars + "|" + "-" * max_chars)

    last_line_number = 0
    for (line_number, diff_found, ans_line, exp_line, ans_chars, exp_chars) in deq:
        num_spaces_after_output = max_chars - ans_chars - max_line_num_digits - 1
        line_number_str = str(line_number) if line_number is not None else ""
        line_num_display = _space_padding(line_number_str, max_line_num_digits - len(line_number_str)) + "|"
        if not diff_found:
            logger.info(utils.NO_HEADER + '%s', line_num_display + _space_padding(ans_line, num_spaces_after_output) + "|" + exp_line)
        else:
            logger.info(utils.NO_HEADER + '%s', line_num_display + utils.red(_space_padding(ans_line, num_spaces_after_output)) + "|" + utils.green(exp_line))
        if line_number is not None:
            last_line_number = line_number
    num_snipped_lines = answer.count('\n') + 1 - last_line_number
    if num_snipped_lines > 0:
        logger.info(utils.NO_HEADER + '... (%s lines) ...', num_snipped_lines)


# TODO: add unit tests for this function, or just remove this function
# TODO: write descripiton for this function. what is the returned value?
def _yield_open_entry(open_entry: Tuple[List[str], List[str], List[int], List[int]]) -> Generator[Tuple[bool, bool, str, str, int, int], None, None]:
    """ Yield all open changes. """
    ls, rs, lnums, rnums = open_entry
    # Get unchanged parts onto the right line
    if ls[0] == rs[0]:
        yield (True, False, ls[0], rs[0], lnums[0], rnums[0])
        for l, r, lnum, rnum in itertools.zip_longest(ls[1:], rs[1:], lnums[1:], rnums[1:]):
            yield (l is not None, True, l or '', r or '', lnum or 0, rnum or 0)
    elif ls[-1] == rs[-1]:
        for l, r, lnum, rnum in itertools.zip_longest(ls[:-1], rs[:-1], lnums[:-1], rnums[:-1]):
            yield (l is not None, l != r, l or '', r or '', lnum or 0, rnum or 0)
        yield (True, False, ls[-1], rs[-1], lnums[-1], rnums[-1])
    else:
        for l, r, lnum, rnum in itertools.zip_longest(ls, rs, lnums, rnums):
            yield (l is not None, True, l or '', r or '', lnum or 0, rnum or 0)


# TODO: add unit tests for this function, or just remove this function
# TODO: write descripiton for this function. what is the argument? what is the returned value?
def _side_by_side_diff(old_text: str, new_text: str) -> Generator[Tuple[bool, bool, str, str, int, int], None, None]:
    """
    Calculates a side-by-side line-based difference view.
    """
    line_split = re.compile(r'(?:\r?\n)')
    dmp = diff_match_patch.diff_match_patch()  # TODO: use difflib instead, if possible

    diff = dmp.diff_main(old_text, new_text)
    dmp.diff_cleanupSemantic(diff)

    open_entry = ([''], [''], [0], [0])
    for change_type, entry in diff:
        assert change_type in [-1, 0, 1]

        entry = (entry.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
        lines = line_split.split(entry)

        # Merge with previous entry if still open
        ls, rs, lnums, rnums = open_entry

        line = lines[0]
        if line:
            if change_type == 0:
                ls[-1] += line
                rs[-1] += line
                lnums[-1] += len(line)
                rnums[-1] += len(line)
            elif change_type == 1:
                rs[-1] = rs[-1] or ''
                rs[-1] += utils.green_diff(line) if line else ''
                rnums[-1] += len(line)
            elif change_type == -1:
                ls[-1] = ls[-1] or ''
                ls[-1] += utils.red_diff(line) if line else ''
                lnums[-1] += len(line)

        lines = lines[1:]

        if lines:
            if change_type == 0:
                # Push out open entry
                yield from _yield_open_entry(open_entry)

                # Directly push out lines until last
                for line in lines[:-1]:
                    yield (True, False, line, line, len(line), len(line))

                # Keep last line open
                open_entry = ([lines[-1]], [lines[-1]], [len(lines[-1])], [len(lines[-1])])
            elif change_type == 1:
                ls, rs, lnums, rnums = open_entry
                for line in lines:
                    rs.append(utils.green_diff(line) if line else '')
                    rnums.append(len(line))
            elif change_type == -1:
                ls, rs, lnums, rnums = open_entry
                for line in lines:
                    ls.append(utils.red_diff(line) if line else '')
                    lnums.append(len(line))

    # Push out open entry
    for entry in _yield_open_entry(open_entry):
        yield entry
