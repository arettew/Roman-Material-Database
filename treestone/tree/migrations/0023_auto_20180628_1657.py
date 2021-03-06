# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-28 16:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tree', '0022_stoneedits'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stones',
            name='name',
            field=models.TextField(blank=True, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='trees',
            name='common_name',
            field=models.TextField(blank=True, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='trees',
            name='sci_name',
            field=models.TextField(blank=True, null=True, unique=True),
        ),
    ]
