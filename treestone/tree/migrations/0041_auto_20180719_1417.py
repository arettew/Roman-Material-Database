# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-19 14:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tree', '0040_auto_20180713_2045'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stoneedits',
            name='image',
        ),
        migrations.RemoveField(
            model_name='treeedits',
            name='image',
        ),
        migrations.AlterField(
            model_name='stoneimages',
            name='img',
            field=models.ImageField(null=True, upload_to='images/stones'),
        ),
        migrations.AlterField(
            model_name='treeimages',
            name='img',
            field=models.ImageField(null=True, upload_to='images/trees'),
        ),
    ]
