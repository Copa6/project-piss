# Generated by Django 2.0.7 on 2018-09-22 13:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('colleges', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('degree', models.CharField(blank=True, default='', max_length=200)),
                ('passing_year', models.IntegerField(default=0)),
                ('number_reviews', models.IntegerField(blank=True, default=0)),
                ('college', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='colleges.College')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserPhoneDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('PHONEWIDTH', models.IntegerField(blank=True, default=1, null=True)),
                ('PHONEHEIGHT', models.IntegerField(blank=True, default=1, null=True)),
                ('imei', models.CharField(blank=True, default='', max_length=350, null=True)),
                ('countryCode', models.CharField(blank=True, default='', max_length=10, null=True)),
                ('OperatorName', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('getSimSerialNumber', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('possibleEmail', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('manufacturer', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('model', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('brand', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('screenresolution', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('dpilevel', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('versionCode', models.CharField(default='0', max_length=10)),
                ('version', models.CharField(default='0', max_length=10)),
                ('serialno', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('phoneid', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('hostid', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('deviceid', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('getSimNumber', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('Mobilenumber', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]