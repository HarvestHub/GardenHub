# Generated by Django 2.0.1 on 2018-01-21 00:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gardenhub', '0004_order_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='pick_all',
            field=models.BooleanField(default=False, help_text='Whether all crops on the physical plot should be picked or not. When checked, the `crops` field is ignored.'),
        ),
        migrations.AlterField(
            model_name='order',
            name='crops',
            field=models.ManyToManyField(blank=True, help_text='Crops that should be picked for this order.', to='gardenhub.Crop'),
        ),
    ]
