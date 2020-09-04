"""This module has unit tests for onlinejudge_command.output_comparators module.
"""

import unittest

from onlinejudge_command.output_comparators import *


class ExactComparatorTest(unittest.TestCase):
    def test_same(self) -> None:
        x = b'Hello, world!'
        y = b'Hello, world!'
        result = True

        compare = ExactComparator()
        self.assertEqual(compare(x, y), result)

    def test_different(self) -> None:
        x = b'Hello, world!'
        y = b'hello world'
        result = False

        compare = ExactComparator()
        self.assertEqual(compare(x, y), result)


class FloatingPointNumberComparatorTest(unittest.TestCase):
    def test_exact_same(self) -> None:
        rel_tol = 0
        abs_tol = 0
        x = b'1.23'
        y = b'1.23'
        result = True

        compare = FloatingPointNumberComparator(rel_tol=rel_tol, abs_tol=abs_tol)
        self.assertEqual(compare(x, y), result)

    def test_relative_close(self) -> None:
        rel_tol = 0.00001
        abs_tol = 0
        x = b'1000000000'
        y = b'1000000007'
        result = True

        compare = FloatingPointNumberComparator(rel_tol=rel_tol, abs_tol=abs_tol)
        self.assertEqual(compare(x, y), result)

    def test_relative_not_close(self) -> None:
        rel_tol = 0.00001
        abs_tol = 0
        x = b'333333336'
        y = b'1000000007'
        result = False

        compare = FloatingPointNumberComparator(rel_tol=rel_tol, abs_tol=abs_tol)
        self.assertEqual(compare(x, y), result)

    def test_absolute_close(self) -> None:
        rel_tol = 0
        abs_tol = 0.001
        x = b'3.142'
        y = b'3.141592'
        result = True

        compare = FloatingPointNumberComparator(rel_tol=rel_tol, abs_tol=abs_tol)
        self.assertEqual(compare(x, y), result)

    def test_absolute_not_close(self) -> None:
        rel_tol = 0
        abs_tol = 0.001
        x = b'3.1415926535'
        y = b'3.0'
        result = False

        compare = FloatingPointNumberComparator(rel_tol=rel_tol, abs_tol=abs_tol)
        self.assertEqual(compare(x, y), result)

    def test_non_float_same(self) -> None:
        rel_tol = 0
        abs_tol = 0
        x = b'foo'
        y = b'foo'
        result = True

        compare = FloatingPointNumberComparator(rel_tol=rel_tol, abs_tol=abs_tol)
        self.assertEqual(compare(x, y), result)

    def test_non_float_diff(self) -> None:
        rel_tol = 0
        abs_tol = 0
        x = b'foo'
        y = b'bar'
        result = False

        compare = FloatingPointNumberComparator(rel_tol=rel_tol, abs_tol=abs_tol)
        self.assertEqual(compare(x, y), result)

    def test_float_and_non_float(self) -> None:
        rel_tol = 0
        abs_tol = 0
        x = b'3.14'
        y = b'pi'
        result = False

        compare = FloatingPointNumberComparator(rel_tol=rel_tol, abs_tol=abs_tol)
        self.assertEqual(compare(x, y), result)


class SplitComparatorTest(unittest.TestCase):
    def test_same(self) -> None:
        x = b'      a  \n b    \r\n\r\n\r\n c \t\t d efg\nxyz \n\n\n   '
        y = b'a b c d efg\nxyz\n'
        result = True

        compare = SplitComparator(ExactComparator())
        self.assertEqual(compare(x, y), result)

    def test_diff(self) -> None:
        x = b'      a  \n b    \r\n\r\n\r\n c \t\t d efg\nxyz \n\n\n   '
        y = b'a b changed deleted efg\nxyz\n'
        result = False

        compare = SplitComparator(ExactComparator())
        self.assertEqual(compare(x, y), result)

    def test_only_spaces(self) -> None:
        x = b'    '
        y = b''
        result = True

        compare = SplitComparator(ExactComparator())
        self.assertEqual(compare(x, y), result)


class SplitLinesComparatorTest(unittest.TestCase):
    def test_same(self) -> None:
        line_comparator = SplitComparator(ExactComparator())
        x = b'a    b    c    d    e\nf\ng\n   xyz   \n'
        y = b'a b c d e\nf\ng\nxyz\n'
        result = True

        compare = SplitLinesComparator(line_comparator)
        self.assertEqual(compare(x, y), result)

    def test_diff(self) -> None:
        line_comparator = SplitComparator(ExactComparator())
        x = b'a b\nc d e\nf\ng\nxyz\n'
        y = b'a b c d e\nf\ng\nxyz\n'
        result = False

        compare = SplitLinesComparator(line_comparator)
        self.assertEqual(compare(x, y), result)

    def test_trailing_spaces(self) -> None:
        line_comparator = SplitComparator(ExactComparator())
        x = b'foo\n    '
        y = b'foo\n'
        result = False

        compare = SplitLinesComparator(line_comparator)
        self.assertEqual(compare(x, y), result)

    def test_no_trailing_newline(self) -> None:
        line_comparator = ExactComparator()
        x = b'foo'
        y = b'foo\n'
        result = True

        compare = SplitLinesComparator(line_comparator)
        self.assertEqual(compare(x, y), result)

    def test_many_trailing_newlines(self) -> None:
        line_comparator = ExactComparator()
        x = b'foo\n\n\n'
        y = b'foo\n'
        result = True

        compare = SplitLinesComparator(line_comparator)
        self.assertEqual(compare(x, y), result)


class CRLFInsensitiveComparatorTest(unittest.TestCase):
    def test_same(self) -> None:
        file_comparator = ExactComparator()
        x = b'foo\r\nbar\r\nbaz\n'
        y = b'foo\nbar\r\nbaz\r\n'
        result = True

        compare = CRLFInsensitiveComparator(file_comparator)
        self.assertEqual(compare(x, y), result)

    def test_diff(self) -> None:
        file_comparator = ExactComparator()
        x = b'foo\r\n'
        y = b'foo\n\n'
        result = False

        compare = CRLFInsensitiveComparator(file_comparator)
        self.assertEqual(compare(x, y), result)
