# Generated by Django 2.0 on 2018-02-27 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orml', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='snapshotmeta',
            name='json_data',
            field=models.TextField(blank=True, null=True),
        ),
    ]
