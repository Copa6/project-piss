from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class College(models.Model):
    id = models.CharField(max_length=200, primary_key=True)
    name = models.CharField(max_length=3000)
    address = models.CharField(max_length=10000, blank=False)
    city = models.CharField(max_length=300, default='')
    state = models.CharField(max_length=300, default='')
    zipcode = models.IntegerField(null=True)
    phoneNumber = models.CharField(max_length=25, blank=True, default='')
    websiteUri = models.CharField(max_length=100, blank=True, default='')
    latitude = models.FloatField(blank=False)
    longitude = models.FloatField(blank=False)
    google_rating = models.FloatField(blank=True, default=0)
    total_rating = models.BigIntegerField(blank=True, default=0)
    number_ratings = models.IntegerField(blank=True, default=0)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    attributions = models.CharField(max_length=200, blank=True, default='')
    city_id = models.CharField(max_length=200, blank=False)
