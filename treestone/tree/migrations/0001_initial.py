# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-26 20:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bibliography',
            fields=[
                ('bibliography_id', models.AutoField(primary_key=True, serialize=False)),
                ('bib_no', models.IntegerField(blank=True, null=True)),
                ('full_citation', models.TextField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Citation',
            fields=[
                ('citation_id', models.AutoField(primary_key=True, serialize=False)),
                ('place_marker', models.TextField(blank=True, null=True)),
                ('page_range', models.TextField(blank=True, null=True)),
                ('classical_identifier', models.TextField(blank=True, null=True)),
                ('url', models.TextField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('bibliography', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='tree.Bibliography')),
            ],
        ),
        migrations.CreateModel(
            name='CitationStone',
            fields=[
                ('citation_stone_id', models.AutoField(primary_key=True, serialize=False)),
                ('supports', models.TextField(blank=True, null=True)),
                ('stone_attribute', models.TextField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('citation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='tree.Citation')),
            ],
        ),
        migrations.CreateModel(
            name='CitationTree',
            fields=[
                ('citation_tree_id', models.AutoField(primary_key=True, serialize=False)),
                ('supports', models.TextField(blank=True, null=True)),
                ('tree_attribute', models.TextField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('citation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='tree.Citation')),
            ],
        ),
        migrations.CreateModel(
            name='Stones',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, null=True)),
                ('alternate_name', models.TextField(blank=True, null=True)),
                ('petrographic_details', models.TextField(blank=True, null=True)),
                ('age', models.TextField(blank=True, null=True)),
                ('appearance', models.TextField(blank=True, null=True)),
                ('poisson_ratio', models.FloatField(blank=True, null=True)),
                ('absorption', models.FloatField(blank=True, null=True)),
                ('quarry_location', models.TextField(blank=True, null=True)),
                ('archaeological_sources', models.TextField(blank=True, null=True)),
                ('primary_sources', models.TextField(blank=True, null=True)),
                ('secondary_sources', models.TextField(blank=True, null=True)),
                ('shapefile', models.TextField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('dates_of_use', models.TextField(blank=True, null=True)),
                ('density_avg', models.FloatField(blank=True, null=True)),
                ('density_low', models.FloatField(blank=True, null=True)),
                ('density_high', models.FloatField(blank=True, null=True)),
                ('elastic_modulus_average', models.FloatField(blank=True, null=True)),
                ('elastic_modulus_low', models.FloatField(blank=True, null=True)),
                ('elastic_modulus_high', models.FloatField(blank=True, null=True)),
                ('image', models.TextField(blank=True, null=True)),
                ('rupture_modulus_average', models.FloatField(blank=True, null=True)),
                ('rupture_modulus_low', models.FloatField(blank=True, null=True)),
                ('rupture_modulus_high', models.FloatField(blank=True, null=True)),
                ('compressive_strength_average', models.FloatField(blank=True, null=True)),
                ('compressive_strength_low', models.FloatField(blank=True, null=True)),
                ('compressive_strength_high', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Trees',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('common_name', models.TextField(blank=True, null=True)),
                ('sci_name', models.TextField(blank=True, null=True)),
                ('distribution', models.TextField(blank=True, null=True)),
                ('tree_rad_low', models.IntegerField(blank=True, null=True)),
                ('tree_rad_high', models.IntegerField(blank=True, null=True)),
                ('density', models.IntegerField(blank=True, null=True)),
                ('janka_hardness', models.IntegerField(blank=True, null=True)),
                ('rupture_modulus', models.IntegerField(blank=True, null=True)),
                ('elastic_modulus', models.IntegerField(blank=True, null=True)),
                ('crushing_strength', models.IntegerField(blank=True, null=True)),
                ('shrink_rad', models.FloatField(blank=True, null=True)),
                ('shrink_tan', models.FloatField(blank=True, null=True)),
                ('shrink_volumetric', models.FloatField(blank=True, null=True)),
                ('rot_resistance', models.TextField(blank=True, null=True)),
                ('workability', models.TextField(blank=True, null=True)),
                ('common_uses', models.TextField(blank=True, null=True)),
                ('primary_sources', models.TextField(blank=True, null=True)),
                ('archaeological_sources', models.TextField(blank=True, null=True)),
                ('shapefile', models.TextField(blank=True, null=True)),
                ('secondary_sources', models.TextField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('tree_height_low', models.FloatField(blank=True, null=True)),
                ('tree_height_high', models.FloatField(blank=True, null=True)),
                ('image', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='citationtree',
            name='tree',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='tree.Trees'),
        ),
        migrations.AddField(
            model_name='citationstone',
            name='stone',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='tree.Stones'),
        ),
    ]
