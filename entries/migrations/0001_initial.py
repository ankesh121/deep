# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-11-06 06:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField()),
                ('name', models.CharField(max_length=70)),
                ('property_name', models.CharField(max_length=70)),
                ('property_pcode', models.CharField(blank=True, default='', max_length=50)),
                ('geojson', models.FileField(upload_to='adminlevels/')),
            ],
            options={
                'ordering': ['country', 'level'],
            },
        ),
        migrations.CreateModel(
            name='AdminLevelSelection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=70)),
                ('pcode', models.CharField(blank=True, default='', max_length=50)),
                ('admin_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entries.AdminLevel')),
            ],
        ),
    ]