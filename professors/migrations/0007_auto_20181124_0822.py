# Generated by Django 2.0.7 on 2018-11-24 08:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('professors', '0006_auto_20181124_0821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='professor',
            name='college',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='current_college', to='colleges.College'),
        ),
    ]
