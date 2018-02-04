from django.db.models import Max, FloatField, Count


def average(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


def max_float(name):
    return Max(name, output_field=FloatField())


def count_distinct(name):
    return Count(name, distinct=True)
