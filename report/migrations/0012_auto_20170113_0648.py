# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-13 06:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0011_auto_20170113_0450'),
    ]

    operations = [
        migrations.AddField(
            model_name='humanprofilefield',
            name='severity_score_total_pin_field',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='peopleinneedfield',
            name='severity_score_total_pin_field',
            field=models.BooleanField(default=False),
        ),
    ]
