# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-27 19:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tree', '0020_treeedits'),
    ]

    operations = [
        migrations.AddField(
            model_name='treeedits',
            name='tree',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tree.Trees'),
        ),
    ]