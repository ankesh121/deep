# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-13 14:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0025_auto_20170313_1403'),
    ]

    operations = [
        migrations.AddField(
            model_name='informationsubpillar',
            name='appear_in',
            field=models.CharField(blank=True, choices=[('PIN', 'People in need'), ('HAC', 'Humanitarian access'), ('HPR', 'Humanitarian profile'), ('KEY', 'Key events')], default=None, max_length=3, null=True),
        ),
    ]
