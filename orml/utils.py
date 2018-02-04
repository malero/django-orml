from django.db.models import Max, FloatField, Count, Aggregate

from orml.helpers import ArgsKwargs


def average(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


def max_float(name):
    return Max(name, output_field=FloatField())


def count_all():
    return Count('*')


def count_distinct(name):
    return Count(name, distinct=True)


def split_queryset_arguments(t):
    values = []
    aggregate_args = []
    aggregate_kwargs = {}

    if type(t) is list:
        for v in t:
            if type(v) is str:
                values.append(v)
            elif isinstance(v, Aggregate):
                aggregate_args.append(v)
    elif type(t) is str:
        values.append(t)
    elif type(t) is dict:
        aggregate_kwargs = t
    elif isinstance(t, Aggregate):
        aggregate_args.append(t)
    elif isinstance(t, ArgsKwargs):
        v, aa, ak = split_queryset_arguments(t.args)
        values += v
        aggregate_args += aa
        aggregate_kwargs.update(ak)
        v, aa, ak = split_queryset_arguments(t.kwargs)
        values += v
        aggregate_args += aa
        aggregate_kwargs.update(ak)

    return values, aggregate_args, aggregate_kwargs
