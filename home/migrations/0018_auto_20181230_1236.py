# Generated by Django 2.0.7 on 2018-12-30 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0017_auto_20181228_0608'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useractivation',
            name='attempt_datetime',
            field=models.FloatField(default=1546173387.88065),
        ),
    ]
