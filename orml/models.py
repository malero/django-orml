from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Query(models.Model):
    name = models.CharField(max_length=128)
    query = models.TextField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class QueryParameter(models.Model):
    INTEGER = 0
    FLOAT = 1
    STRING = 2
    DATE = 3
    OTHER = 1000

    TYPE_CHOICES = (
        (INTEGER, 'Integer'),
        (FLOAT, 'Float'),
        (STRING, 'String'),
        (DATE, 'Date'),
        (OTHER, 'Other'),
    )

    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    variable = models.CharField(max_length=32)
    default = models.CharField(max_length=250)
    is_array = models.BooleanField(default=False)
    param_type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)

    def __str__(self):
        return self.name


class Snapshot(models.Model):
    name = models.CharField(max_length=32)
    namespace = models.CharField(max_length=32)
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    save_meta = models.BooleanField(default=False)
    meta_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                          null=True, blank=True)
    meta_object_key = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return self.name


class SnapshotMeta(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    obj = GenericForeignKey('content_type', 'object_id')
    json_data = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = (('content_type', 'object_id'),)
