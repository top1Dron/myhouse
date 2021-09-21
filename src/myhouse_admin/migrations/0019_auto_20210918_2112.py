# Generated by Django 3.2.5 on 2021-09-18 18:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('myhouse_admin', '0018_alter_meterreading_reading_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='receipt',
            name='tariff',
        ),
        migrations.AddField(
            model_name='ticket',
            name='added_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
