# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-23 06:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0014_auto_20161122_1049'),
    ]

    operations = [
        migrations.AddField(
            model_name='sector',
            name='icon',
            field=models.FileField(blank=True, default=None, null=True, upload_to='sector-icons/'),
        ),
    ]