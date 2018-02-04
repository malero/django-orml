# Django Object Relational Mapping Language

django-orml is a simple querying language for the Django ORM. Initial syntax implementation is focused on saving and executing simple queries for report building. It is not yet completed, but here is some current and upcoming syntax:

### Currently Implemented Syntax

**Simple ORM filter**
```
# Will return <QuerySet [<MyModel object (1)>, <MyModel object (3)>]>
my_app.mymodel{id__in:(1,3)}
```

**Queries with | operator**
```
# Will return all MyModel instances with "term" in the name or description
my_app.mymodel{name__icontains: "term" | description__icontains: "term"}
```

**Nested Queries**
```
# Will return children of MyModel with id of 1 and 3
my_app.mymodelchild{parent__in:(my_app.mymodel{id__in:(1,3)})}
```

```
# Same query on multiple lines
parents = my_app.mymodel{id__in:(1,3)}
my_app.mymodelchild{parent__in:parents}
```

### Upcoming Features

* Date values
* Aggregation and annotation
