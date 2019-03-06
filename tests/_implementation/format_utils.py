import unittest

from onlinejudge._implementation.format_utils import *


class PercentFormatTest(unittest.TestCase):
    def test_percentformat(self):
        self.assertEqual(percentformat("foo %a%a bar %b", {"a": "AA", "b": "12345"}), 'foo AAAA bar 12345')
        self.assertEqual(percentformat("foo %%a bar %%%a %b", {"a": "%a%b", "b": "12345"}), 'foo %a bar %%a%b 12345')
        self.assertRaises(KeyError, lambda: percentformat("%z", {}))

    def test_percentparse(self):
        self.assertEqual(percentparse("foo AAAA bar 12345", "foo %a%a bar %b", {"a": "AA", "b": "12345"}), {'a': 'AA', 'b': '12345'})
        self.assertEqual(percentparse("123456789", "%x%y%z", {"x": r"\d+", "y": r"\d", "z": r"(\d\d\d)+"}), {'x': '12345', 'y': '6', 'z': '789'})
        self.assertRaises(KeyError, lambda: percentparse("foo", "%a", {}))
