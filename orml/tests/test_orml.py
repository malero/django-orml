from django.test import TestCase

from orml import parser


class TestORML(TestCase):
    def test_lists(self):
        a = parser.parse('1,2,3')
        self.assertEqual(a, [1,2,3,])

    def test_sum_with_list(self):
        a = parser.parse('SUM(1,2,3)')
        self.assertEqual(6, a)

    def test_avg_with_list(self):
        a = parser.parse('AVG(0,5,10)')
        self.assertEqual(a, 5)
