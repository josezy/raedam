# Generated by Django 2.2.6 on 2019-10-20 00:30

import django.contrib.postgres.fields
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ParkingCamera',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('url', models.URLField(unique=True)),
                ('geopoint', models.CharField(max_length=100)),
                ('spots', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), size=4), default=list, size=None)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]