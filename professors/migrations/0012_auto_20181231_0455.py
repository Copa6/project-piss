# Generated by Django 2.0.7 on 2018-12-31 04:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('professors', '0011_auto_20181230_1236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='professor',
            name='department',
            field=models.CharField(max_length=1500),
        ),
        migrations.AlterField(
            model_name='professor',
            name='designation',
            field=models.CharField(blank=True, default='', max_length=1500),
        ),
        migrations.AlterField(
            model_name='professor',
            name='qualifications',
            field=models.CharField(blank=True, default='', max_length=3000),
        ),
        migrations.AlterField(
            model_name='review',
            name='review',
            field=models.CharField(blank=True, default='', max_length=3000),
        ),
        migrations.AlterField(
            model_name='review',
            name='title',
            field=models.CharField(default='-----', max_length=1000),
        ),
    ]
