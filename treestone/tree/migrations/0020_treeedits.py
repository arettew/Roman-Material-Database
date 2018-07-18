# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-27 15:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tree', '0019_auto_20180626_1932'),
    ]

    operations = [
        migrations.CreateModel(
            name='TreeEdits',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('common_name', models.TextField(blank=True, null=True)),
                ('sci_name', models.TextField(blank=True, null=True)),
                ('distribution', models.TextField(blank=True, null=True)),
                ('tree_rad_low', models.FloatField(blank=True, null=True)),
                ('tree_rad_high', models.FloatField(blank=True, null=True)),
                ('density', models.FloatField(blank=True, null=True)),
                ('janka_hardness', models.FloatField(blank=True, null=True)),
                ('rupture_modulus', models.FloatField(blank=True, null=True)),
                ('elastic_modulus', models.FloatField(blank=True, null=True)),
                ('crushing_strength', models.FloatField(blank=True, null=True)),
                ('shrink_rad', models.FloatField(blank=True, null=True)),
                ('shrink_tan', models.FloatField(blank=True, null=True)),
                ('shrink_volumetric', models.FloatField(blank=True, null=True)),
                ('rot_resistance', models.TextField(blank=True, null=True)),
                ('workability', models.TextField(blank=True, null=True)),
                ('common_uses', models.TextField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('tree_height_low', models.FloatField(blank=True, null=True)),
                ('tree_height_high', models.FloatField(blank=True, null=True)),
            ],
        ),
    ]