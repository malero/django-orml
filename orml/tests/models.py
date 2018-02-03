from django.db import models


class TestModel(models.Model):
    T1 = 0
    T2 = 1
    T3 = 2

    T_CHOICES = (
        (T1, 'T1'),
        (T2, 'T2'),
        (T3, 'T3'),
    )
    t = models.PositiveSmallIntegerField(choices=T_CHOICES)
    val = models.IntegerField()
    note = models.CharField(max_length=50, null=True)


class TestModelChild(models.Model):
    parent = models.ForeignKey(TestModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
