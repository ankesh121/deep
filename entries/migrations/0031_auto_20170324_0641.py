# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-24 06:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0030_auto_20170324_0555'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entrytemplate',
            name='elements',
            field=models.TextField(default='[]'),
        ),
    ]