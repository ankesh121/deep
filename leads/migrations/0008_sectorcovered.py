# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-10-08 06:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0007_auto_20161008_0558'),
    ]

    operations = [
        migrations.CreateModel(
            name='SectorCovered',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
    ]