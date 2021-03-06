# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-11-06 06:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('entries', '0001_initial'),
        ('leads', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='adminlevel',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='leads.Country'),
        ),
        migrations.AlterUniqueTogether(
            name='adminlevelselection',
            unique_together=set([('admin_level', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='adminlevel',
            unique_together=set([('country', 'level')]),
        ),
    ]
