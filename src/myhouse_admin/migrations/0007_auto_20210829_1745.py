# Generated by Django 3.2.5 on 2021-08-29 14:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myhouse_admin', '0006_auto_20210804_1552'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='house',
            options={'ordering': ('name',)},
        ),
        migrations.AlterUniqueTogether(
            name='floor',
            unique_together={('name', 'section')},
        ),
        migrations.AlterUniqueTogether(
            name='house',
            unique_together={('name', 'address')},
        ),
        migrations.AlterUniqueTogether(
            name='section',
            unique_together={('name', 'house')},
        ),
    ]