import unittest

from onlinejudge.implementation.command.code_statistics import get_statistics

class CodeStatisticsTest(unittest.TestCase):

    def test_get_statistics_1(self):
        # http://golf.shinh.org/reveal.rb?Turn+a+1d+array+into+a+5d+array/mitchs+%28cheat%29_1465127634&bf
        code = b'''<-],<[->>[.<]>>>.,+]\x00 ;\x01e\x0b'''
        stat = get_statistics(code)
        self.assertEqual(stat['binary'], 3)
        self.assertEqual(stat['alnum'], 1)
        self.assertEqual(stat['symbol'], 21)

    def test_get_statistics_2(self):
        # http://golf.shinh.org/reveal.rb?DozzFizzBuzz/%2520_1434433980
        code = b'''\
\x01oiuea1.>g1+00p25*,>:00g\\2g%#v_:6%1g,:5%1v
DFBMPQ@_^#`"c"g  $_^#`"\x18": +1<,,"zz" ,g0+<
\x02\x03\x05\x07\x0b\x0d\x11\x13\x17\x1d\x1f%)+/5;=CGIOSYa'''
        stat = get_statistics(code)
        self.assertEqual(stat['binary'], 13)
        self.assertEqual(stat['alnum'], 46)
        self.assertEqual(stat['symbol'], 46)
