# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-26 05:17
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('usergroup', '0005_auto_20170223_1054'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergroup',
            name='owner',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='groups_superowned', to=settings.AUTH_USER_MODEL),
        ),
    ]
