# Django Object Relational Mapping Language

django-orml is a simple querying language for the Django ORM. Initial syntax implementation is focused on saving and executing simple queries for report building. It is not yet completed, but here is some current and upcoming syntax:

### Instalation

```pip install django-orml```

### Currently Implemented Syntax

**Simple ORM filter**

Will return <QuerySet [<MyModel object (1)>, <MyModel object (3)>]>
```
my_app.mymodel{id__in:(1,3)}
```

**Queries with | operator**

Will return all MyModel instances with "term" in the name or description
```
my_app.mymodel{name__icontains: "term" | description__icontains: "term"}
```

**Nested Queries**
Will return children of MyModel with id of 1 and 3
```
my_app.mymodelchild{parent__in:(my_app.mymodel{id__in:(1,3)})}
```

Same query on multiple lines
```
parents = my_app.mymodel{id__in:(1,3)}
my_app.mymodelchild{parent__in:parents}
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
