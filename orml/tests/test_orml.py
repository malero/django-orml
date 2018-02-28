from unittest import skip

from django.test import TestCase

from orml import parser
from orml.tests.models import TestModel, TestModelChild


class TestORML(TestCase):
    def test_ints(self):
        a = parser.parse('1')
        self.assertEqual(a, 1)

    def test_floats(self):
        a = parser.parse('1.49')
        self.assertEqual(a, 1.49)

    def test_strings(self):
        a = parser.parse('"string test"')
        self.assertEqual(a, 'string test')

    def test_assignments(self):
        a = parser.parse([
            'a__in=5',
            'a__in'
        ])

    def test_lists(self):
        a = parser.parse('[1,2,3]')
        self.assertEqual(a, [1,2,3,])

    def test_dicts(self):
        d = parser.parse('{a:1,b:2,c:3}')
        self.assertEqual(d['a'], 1)
        self.assertEqual(d['b'], 2)
        self.assertEqual(d['c'], 3)

    def test_assigned_dicts(self):
        v = parser.parse([
            'a = {a:1,b:2,c:3}',
            'a.b'
        ])
        self.assertEqual(v, 2)

    def test_dict_list(self):
        d = parser.parse('{a:[1,2,3],b:[2,3,4],c:[3,4,5]}')
        self.assertEqual(d['a'], [1,2,3])
        self.assertEqual(d['b'], [2,3,4])
        self.assertEqual(d['c'], [3,4,5])

    def test_piped_dict(self):
        d = parser.parse([
            'a=[{a:1,b:2}, {a:15,b:30}, {a:50,b:100}, {a:500,b:1000}]',
            'a@b'
        ])
        self.assertEqual(d, [2, 30, 100, 1000])

    @skip("does not work, will have to be implemented later")
    def test_piped_list(self):
        d = parser.parse([
            '[[1,2,3], [2,3,4], [3,4,5], [4,5,6]]'
        ])
        self.assertEqual(d, [1, 2, 3, 4])

    def test_sum_with_list(self):
        a = parser.parse('sum([1,2,3])')
        self.assertEqual(6, a)

    def test_avg_with_list(self):
        a = parser.parse('average([0,5,10])')
        self.assertEqual(a, 5)

    def test_equals(self):
        self.assertTrue(parser.parse('5+5*5==30'))

    def test_blocks(self):
        a = parser.parse([
            'a=2',
            'a*15'
        ])
        self.assertEqual(a, 30)

    def test_model_resolution(self):
        model = parser.parse('tests.testmodel')
        self.assertEqual(TestModel, model)

    def test_querychain(self):
        a = parser.parse('{id:3} | {val:15, id:2} | {id:1}')

    def test_model_filtering(self):
        test_1 = TestModel.objects.create(
            t=TestModel.T1,
            val=15,
            note='Test Model 1'
        )
        test_2 = TestModel.objects.create(
            t=TestModel.T1,
            val=100,
            note='Test Model 2'
        )
        test_3 = TestModel.objects.create(
            t=TestModel.T2,
            val=1,
            note='Test Model 3'
        )

        test_3_child = TestModelChild.objects.create(
            parent=test_3,
            name="Test Model 3 Child"
        )

        query_1 = parser.parse('tests.testmodel{id: 1}')
        self.assertEqual(test_1, query_1[0])

        query_2 = parser.parse('tests.testmodel{id: 2}')
        self.assertEqual(test_2, query_2[0])

        query_3 = parser.parse('tests.testmodel{id: 3}')
        self.assertEqual(test_3, query_3[0])

        query_4 = parser.parse('tests.testmodel{id__in: [1,3]}')
        self.assertEqual(len(query_4), 2)

        # Test accessor to value list on QuerySet
        query_5 = parser.parse('tests.testmodel{id__in: [1,3]}[id]')
        self.assertEqual(query_5[0]['id'], 1)
        self.assertEqual(query_5[1]['id'], 3)

        # Test multi accessor to dict[] on a QuerySet
        query_6 = parser.parse('tests.testmodel{id__in: [1,3]}[t, val, note]')
        self.assertEqual(query_6[0]['t'], test_1.t)
        self.assertEqual(query_6[0]['val'], test_1.val)
        self.assertEqual(query_6[0]['note'], test_1.note)

        self.assertEqual(query_6[1]['t'], test_3.t)
        self.assertEqual(query_6[1]['val'], test_3.val)
        self.assertEqual(query_6[1]['note'], test_3.note)

        # Nested queries and multiple statements (same query written 3 different ways)
        query_7 = parser.parse('tests.testmodelchild{parent__in: (tests.testmodel{id__in:[1,3]}[id]@id)}')
        query_8 = parser.parse([
            'parent_ids=tests.testmodel{id__in:[1,3]}[id]',
            'tests.testmodelchild{parent__in:parent_ids}'
        ])
        query_9 = parser.parse('tests.testmodelchild{parent_id__in: [1,3]}')
        self.assertEqual(query_9[0], query_7[0])
        self.assertEqual(query_9[0], query_8[0])

        # Testing icontains, for fun
        query_10 = parser.parse('tests.testmodel{note__icontains: "test model"}[id]')
        ids = [t['id'] for t in query_10]
        self.assertIn(1, ids)
        self.assertIn(2, ids)
        self.assertIn(3, ids)
        self.assertEqual(len(ids), 3)

    def test_aggregates(self):
        test_1 = TestModel.objects.create(
            t=TestModel.T1,
            val=10,
            note='Test Model 1'
        )
        test_2 = TestModel.objects.create(
            t=TestModel.T1,
            val=30,
            note='Test Model 2'
        )
        test_3 = TestModel.objects.create(
            t=TestModel.T2,
            val=50,
            note='Test Model 3'
        )

        a = parser.parse(["""
            tests.testmodel{note__icontains: "test model"}
            [{
                diff: (MaxFloat(val) - Avg(val)),
                avg: Avg(val),
                sum: Sum(val),
                min: Min(val),
                max: Max(val),
                count: Count(id),
                t_distinct: CountDistinct(t)
            }]""", ])
        self.assertEqual(a['diff'], 20.0)
        self.assertEqual(a['avg'], 30)
        self.assertEqual(a['sum'], 90)
        self.assertEqual(a['min'], 10)
        self.assertEqual(a['max'], 50)
        self.assertEqual(a['count'], 3)
        self.assertEqual(a['t_distinct'], 2)

    def test_argskwargs(self):
        test_1 = TestModel.objects.create(
            t=TestModel.T1,
            val=10,
            note='Test Model 1'
        )
        test_2 = TestModel.objects.create(
            t=TestModel.T1,
            val=30,
            note='Test Model 2'
        )
        test_3 = TestModel.objects.create(
            t=TestModel.T2,
            val=50,
            note='Test Model 3'
        )

        a = parser.parse(["""
            tests.testmodel{note__icontains: "test model"}
            [
                Avg(val),
                Sum(val),
                min: Min(val),
                max: Max(val)
            ]""", ])

        self.assertEqual(a['val__avg'], 30)
        self.assertEqual(a['val__sum'], 90)
        self.assertEqual(a['min'], 10)
        self.assertEqual(a['max'], 50)

    def test_distinct(self):
        test_1 = TestModel.objects.create(
            t=TestModel.T1,
            val=10,
            note='Test Model 1'
        )
        test_2 = TestModel.objects.create(
            t=TestModel.T1,
            val=30,
            note='Test Model 2'
        )
        test_3 = TestModel.objects.create(
            t=TestModel.T2,
            val=50,
            note='Test Model 3'
        )

        a = parser.parse(["""
            tests.testmodel{note__icontains: "test model"}
            [
                distinct,
                t,
                avg: Avg(val),
                count: Count("*")
            ]""", ])
        self.assertEqual(len(a), 2)
        for r in a:
            if r['t'] == TestModel.T1:
                self.assertEqual(r['avg'], 20.0)
                self.assertEqual(r['count'], 2)
            else:
                self.assertEqual(r['avg'], 50.0)
                self.assertEqual(r['count'], 1)
