from django.contrib import admin

from orml.models import Query, Snapshot, QueryParameter, SnapshotMeta


@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    raw_id_fields = ['creator', ]


@admin.register(QueryParameter)
class QueryParameterAdmin(admin.ModelAdmin):
    pass


@admin.register(Snapshot)
class SnapshotAdmin(admin.ModelAdmin):
    pass


@admin.register(SnapshotMeta)
class SnapshotMetaAdmin(admin.ModelAdmin):
    pass
