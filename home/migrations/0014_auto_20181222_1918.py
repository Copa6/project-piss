# Generated by Django 2.0.7 on 2018-12-22 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0013_auto_20181124_0822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useractivation',
            name='attempt_datetime',
            field=models.FloatField(default=1545506293.396854),
        ),
    ]
