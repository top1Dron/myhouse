# Generated by Django 3.2.5 on 2021-09-13 15:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myhouse_admin', '0013_alter_cashboxrecord_summary'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cashboxrecord',
            options={'ordering': ('-date',)},
        ),
        migrations.RemoveField(
            model_name='cashboxrecord',
            name='owner',
        ),
    ]