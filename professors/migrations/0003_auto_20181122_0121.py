# Generated by Django 2.0.7 on 2018-11-22 01:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('professors', '0002_review_title'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='user',
            new_name='added_by',
        ),
    ]