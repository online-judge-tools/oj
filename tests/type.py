import unittest

from onlinejudge.type import Problem, Service, Submission


class TypeTest(unittest.TestCase):
    def test_instantiate_abstract_class(self):
        self.assertRaises(TypeError, Service)
        self.assertRaises(TypeError, Problem)
        self.assertRaises(TypeError, Submission)
