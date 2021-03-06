# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-11-07 06:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0003_auto_20161106_0732'),
    ]

    operations = [
        migrations.AddField(
            model_name='entryinformation',
            name='affected_groups',
            field=models.ManyToManyField(blank=True, to='entries.AffectedGroup'),
        ),
        migrations.AddField(
            model_name='entryinformation',
            name='map_selections',
            field=models.ManyToManyField(blank=True, to='entries.AdminLevelSelection'),
        ),
        migrations.AddField(
            model_name='entryinformation',
            name='number',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='entryinformation',
            name='specific_needs_groups',
            field=models.ManyToManyField(blank=True, to='entries.SpecificNeedsGroup'),
        ),
        migrations.AddField(
            model_name='entryinformation',
            name='vulnerable_groups',
            field=models.ManyToManyField(blank=True, to='entries.VulnerableGroup'),
        ),
        migrations.AddField(
            model_name='subsector',
            name='sector',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='entries.Sector'),
            preserve_default=False,
        ),
    ]
