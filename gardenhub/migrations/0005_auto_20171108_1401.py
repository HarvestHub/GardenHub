# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-08 19:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gardenhub', '0004_auto_20171105_2239'),
    ]

    operations = [
        migrations.RenameField(
            model_name='plot',
            old_name='gardener',
            new_name='gardeners',
        ),
    ]