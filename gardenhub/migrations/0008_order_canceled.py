# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-26 20:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gardenhub', '0007_auto_20171109_1129'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='canceled',
            field=models.BooleanField(default=False),
        ),
    ]