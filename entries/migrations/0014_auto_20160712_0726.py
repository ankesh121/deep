# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-07-12 07:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0013_auto_20160712_0420'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entry',
            name='country',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='crisis_drivers',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='excerpt',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='information_at',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='map_data',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='problem_timeline',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='reliability',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='sectors',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='severity',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='status',
        ),
        migrations.RemoveField(
            model_name='entry',
            name='underlying_factors',
        ),
    ]
