# Generated by Django 2.0.7 on 2018-12-28 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0015_auto_20181223_1156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useractivation',
            name='attempt_datetime',
            field=models.FloatField(default=1545977167.823219),
        ),
    ]