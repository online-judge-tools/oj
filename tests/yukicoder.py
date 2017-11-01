import unittest

from onlinejudge.yukicoder import YukicoderService

class YukicoderTest(unittest.TestCase):

    def test_get_user_10(self):
        data = YukicoderService().get_user(id=10)
        self.assertEqual(data['Id'], 10)
        self.assertEqual(data['Name'], 'yuki2006')
    def test_get_user_yuki2006(self):
        data = YukicoderService().get_user(name='yuki2006')
        self.assertEqual(data['Id'], 10)
        self.assertEqual(data['Name'], 'yuki2006')
    def test_get_user_0(self):
        data = YukicoderService().get_user(id=0)
        self.assertIs(data, None)


if __name__ == '__main__':
    unittest.main()
