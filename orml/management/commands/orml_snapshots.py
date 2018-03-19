import json

from django.core.management.base import BaseCommand
from django.db.models.base import ModelBase
from django.forms import model_to_dict

from orml.models import Snapshot, SnapshotMeta
from orml.parser import parse


class Command(BaseCommand):
    help = 'Run snapshots and saves snapshot meta data'

    def handle(self, *args, **options):
        for snapshot in Snapshot.objects.select_related('query').filter(save_meta=True):
            try:
                result = parse(snapshot.query.query)
                for r in result:
                    if isinstance(r, ModelBase):
                        r = model_to_dict(r)
                    snapshot_meta, created = SnapshotMeta.objects.get_or_create(
                        content_type=snapshot.meta_content_type,
                        object_id=r.get(snapshot.meta_object_key)
                    )
                    try:
                        json_data = json.loads(snapshot_meta.json_data)
                    except json.JSONDecodeError:
                        json_data = {}
                    if snapshot.namespace not in json_data:
                        json_data[snapshot.namespace] = {}
                    json_data[snapshot.namespace].update(r)
                    snapshot_meta.json_data = json.dumps(json_data)
                    snapshot_meta.save()
            except SyntaxError:
                print('Syntax error: #{}'.format(snapshot.query_id))
