import datetime
import time

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from professors.models import Professor
from django.contrib.auth.models import User, AbstractUser

from colleges.models import College


# Create your models here.
from project_piss import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, college=None, password=None):
        if not email:
            raise ValueError('Email must be set!')
        user = self.model(email=email, username=username, college=college)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, college=None, password=None):
        user = self.create_user(email, username, college=None, password=password)
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class UserActivation(models.Model):

    email = models.CharField(max_length=300, primary_key=True)
    activation_code = models.IntegerField(blank=False)
    activation_status = models.BooleanField(blank=False)
    num_attempts = models.IntegerField(blank=False, default=0)
    attempt_datetime = models.FloatField(blank=False, default=time.time())


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now_add=True)
    college = models.ForeignKey(College, on_delete=models.CASCADE, blank=True, null=True)
    degree = models.CharField(max_length=200, blank=True, default='')
    passing_year = models.IntegerField(default=0000, blank=True)
    number_reviews = models.IntegerField(blank=True, default=0)


class UserPhoneDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    PHONEWIDTH = models.IntegerField(blank=True, default=1, null=True)
    PHONEHEIGHT = models.IntegerField(blank=True, default=1, null=True)
    imei = models.CharField(max_length=350, blank=True, default='', null=True)
    countryCode = models.CharField(max_length=10, blank=True, default='', null=True)
    OperatorName = models.CharField(max_length=100, blank=True, default='', null=True)
    getSimSerialNumber = models.CharField(max_length=100, blank=True, default='', null=True)
    possibleEmail = models.CharField(max_length=100, blank=True, default='', null=True)
    manufacturer = models.CharField(max_length=100, blank=True, default='', null=True)
    model = models.CharField(max_length=100, blank=True, default='', null=True)
    brand = models.CharField(max_length=100, blank=True, default='', null=True)
    screenresolution = models.CharField(max_length=100, blank=True, default='', null=True)
    dpilevel = models.CharField(max_length=100, blank=True, default='', null=True)
    osversion = models.CharField(max_length=100, blank=True, default='', null=True),
    versionCode = models.CharField(max_length=10, blank=False, default="0")
    version = models.CharField(max_length=10, blank=False, default="0")
    serialno = models.CharField(max_length=100, blank=True, default='', null=True)
    phoneid = models.CharField(max_length=100, blank=True, default='', null=True)
    hostid = models.CharField(max_length=100, blank=True, default='', null=True)
    deviceid = models.CharField(max_length=100, blank=True, default='', null=True)
    getSimNumber = models.CharField(max_length=100, blank=True, default='', null=True)
    Mobilenumber = models.CharField(max_length=100, blank=True, default='', null=True)

