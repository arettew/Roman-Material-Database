# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-29 21:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tree', '0027_treeedits_citation'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stoneedits',
            old_name='stone',
            new_name='main_object',
        ),
        migrations.RenameField(
            model_name='treeedits',
            old_name='tree',
            new_name='main_object',
        ),
    ]
