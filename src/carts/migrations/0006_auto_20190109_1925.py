# Generated by Django 2.1.4 on 2019-01-09 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0005_auto_20190109_1920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='sub_total',
            field=models.DecimalField(decimal_places=2, max_digits=100, null=True),
        ),
    ]
