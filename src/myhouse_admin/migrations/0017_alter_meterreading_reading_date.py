# Generated by Django 3.2.5 on 2021-09-15 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myhouse_admin', '0016_meterreading_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meterreading',
            name='reading_date',
            field=models.DateTimeField(),
        ),
    ]
