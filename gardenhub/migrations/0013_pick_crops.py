# Generated by Django 2.0 on 2017-12-28 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gardenhub', '0012_auto_20171220_1209'),
    ]

    operations = [
        migrations.AddField(
            model_name='pick',
            name='crops',
            field=models.ManyToManyField(to='gardenhub.Crop'),
        ),
    ]
