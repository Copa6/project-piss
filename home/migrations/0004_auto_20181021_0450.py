# Generated by Django 2.0.7 on 2018-10-21 04:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_useractivation_activation_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='useractivation',
            name='atempt_datetime',
            field=models.FloatField(default=1540097454.9375196),
        ),
        migrations.AddField(
            model_name='useractivation',
            name='num_attempts',
            field=models.IntegerField(default=0),
        ),
    ]