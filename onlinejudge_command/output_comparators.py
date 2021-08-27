"""This module collects helper classes to compare outputs for `test` subcommand.
"""

import abc
import enum
import math
from logging import getLogger
from typing import *

logger = getLogger(__name__)


class OutputComparator(abc.ABC):
    @abc.abstractmethod
    def __call__(self, actual: bytes, expected: bytes) -> bool:
        """
        :returns: True is the two are matched.
        """
        raise NotImplementedError


class ExactComparator(OutputComparator):
    def __call__(self, actual: bytes, expected: bytes) -> bool:
        return actual == expected


class FloatingPointNumberComparator(OutputComparator):
    def __init__(self, *, rel_tol: float, abs_tol: float):
        if max(rel_tol, abs_tol) > 1:
            logger.warning('the tolerance is too large: relative = %s, absolute = %s', rel_tol, abs_tol)
        self.rel_tol = rel_tol
        self.abs_tol = abs_tol

    def __call__(self, actual: bytes, expected: bytes) -> bool:
        """
        :returns: True if the relative error or absolute error is smaller than the accepted error
        """
        try:
            x: Optional[float] = float(actual)
        except ValueError:
            x = None
        try:
            y: Optional[float] = float(expected)
        except ValueError:
            y = None
        if x is not None and y is not None:
            return math.isclose(x, y, rel_tol=self.rel_tol, abs_tol=self.abs_tol)
        else:
            return actual == expected


class SplitComparator(OutputComparator):
    def __init__(self, word_comparator: OutputComparator):
        self.word_comparator = word_comparator

    def __call__(self, actual: bytes, expected: bytes) -> bool:
        # str.split() also removes trailing '\r'
        actual_words = actual.split()
        expected_words = expected.split()
        if len(actual_words) != len(expected_words):
            return False
        for x, y in zip(actual_words, expected_words):
            if not self.word_comparator(x, y):
                return False
        return True


class SplitLinesComparator(OutputComparator):
    def __init__(self, line_comparator: OutputComparator):
        self.line_comparator = line_comparator

    def __call__(self, actual: bytes, expected: bytes) -> bool:
        actual_lines = actual.rstrip(b'\n').split(b'\n')
        expected_lines = expected.rstrip(b'\n').split(b'\n')
        if len(actual_lines) != len(expected_lines):
            return False
        for x, y in zip(actual_lines, expected_lines):
            if not self.line_comparator(x, y):
                return False
        return True


class CRLFInsensitiveComparator(OutputComparator):
    def __init__(self, file_comparator: OutputComparator):
        self.file_comparator = file_comparator

    def __call__(self, actual: bytes, expected: bytes) -> bool:
        return self.file_comparator(actual.replace(b'\r\n', b'\n'), expected.replace(b'\r\n', b'\n'))


class CompareMode(enum.Enum):
    EXACT_MATCH = 'exact-match'
    CRLF_INSENSITIVE_EXACT_MATCH = 'crlf-insensitive-exact-match'
    IGNORE_SPACES = 'ignore-spaces'
    IGNORE_SPACES_AND_NEWLINES = 'ignore-spaces-and-newlines'


# This function is used from onlinejudge_command.pretty_printers.
def check_lines_match(a: str, b: str, *, compare_mode: CompareMode) -> bool:
    if compare_mode == CompareMode.EXACT_MATCH:
        comparator: OutputComparator = ExactComparator()
    elif compare_mode == CompareMode.CRLF_INSENSITIVE_EXACT_MATCH:
        comparator = CRLFInsensitiveComparator(ExactComparator())
    elif compare_mode == CompareMode.IGNORE_SPACES:
        comparator = SplitComparator(ExactComparator())
    elif compare_mode == CompareMode.IGNORE_SPACES_AND_NEWLINES:
        raise RuntimeError('CompareMode.IGNORE_SPACES_AND_NEWLINES is not allowed for this function')
    else:
        assert False
    return comparator(a.encode(), b.encode())
