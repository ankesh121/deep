# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-09 06:47
from __future__ import unicode_literals

from django.db import migrations


def migrate_assignee(apps, schema_editor):
    Event = apps.get_model("leads", "Event")
    for event in Event.objects.all():
        if event.assigned_to:
            event.assignee.add(event.assigned_to)


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0008_auto_20161209_0647'),
    ]

    operations = [
        migrations.RunPython(migrate_assignee)
    ]
