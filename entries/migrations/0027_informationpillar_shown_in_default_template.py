# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-22 06:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0026_informationsubpillar_appear_in'),
    ]

    operations = [
        migrations.AddField(
            model_name='informationpillar',
            name='shown_in_default_template',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]
