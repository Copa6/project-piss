# Generated by Django 2.0.7 on 2018-09-27 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserActivation',
            fields=[
                ('email', models.CharField(max_length=300, primary_key=True, serialize=False)),
                ('activation_code', models.IntegerField()),
            ],
        ),
    ]