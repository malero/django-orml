# Django Object Relational Mapping Language

django-orml is a simple querying language for the Django ORM. Initial syntax implementation is focused on saving and executing simple queries for report building. It is not yet completed, but here is some current and upcoming syntax:

### Currently Implemented Syntax

**Simple ORM filter**

Will return list of dicts with data for MyModel.pk 1 and 3
```
my_app.mymodel{id__in:(1,3)}
```

**Queries with | operator**

Will return all MyModel instances with "term" in the name or description
```
my_app.mymodel{name__icontains: "term" | description__icontains: "term"}
```

**Aggregation and Annotation**

Get average, sum, min and max values
```
tests.testmodel{note__icontains: "test model"}
    [
        Avg(value),
        Sum(value),
        min: Min(value),
        max: Max(value)
    ]
```

Distinct query, grouped by transaction type, count and average of values field
```
tests.testmodel{client_id=15}
    [
        distinct,
        transaction_type,
        avg: Avg(value),
        count: Count("*")
    ]
```

### Upcoming Features

* Date values
* Model permissions based on Django Auth Groups/Permissions


### Instalation

```pip install django-orml```