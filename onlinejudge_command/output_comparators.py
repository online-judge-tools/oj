"""This module collects helper classes to compare outputs for `test` subcommand.
"""

import abc
import math
import pathlib
import tempfile
from logging import getLogger
from typing import *

import onlinejudge_command.pretty_printers as pretty_printers
import onlinejudge_command.utils as utils

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


class SpecialJudge:
    def __init__(self, judge_command: str, *, is_silent: bool):
        self.judge_command = judge_command  # already quoted and joined command
        self.is_silent = is_silent

    def run(self, *, actual_output: bytes, input_path: pathlib.Path, expected_output_path: Optional[pathlib.Path]) -> bool:
        with tempfile.TemporaryDirectory() as tempdir:
            actual_output_path = pathlib.Path(tempdir) / 'actual.out'
            with open(actual_output_path, 'wb') as fh:
                fh.write(actual_output)

            # if you use shlex.quote, it fails on Windows. why?
            command = ' '.join([
                self.judge_command,  # already quoted and joined command
                str(input_path.resolve()),
                str(actual_output_path.resolve()),
                str(expected_output_path.resolve() if expected_output_path is not None else ''),
            ])

            logger.info('$ %s', command)
            info, proc = utils.exec_command(command)
        if not self.is_silent:
            logger.info(utils.NO_HEADER + 'judge\'s output:\n%s', pretty_printers.make_pretty_large_file_content(info['answer'] or b'', limit=40, head=20, tail=10, bold=True))
        return proc.returncode == 0
