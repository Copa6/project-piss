from django.contrib.auth.models import User
from rest_framework import serializers
from .models import College


class CollegesSerializerPOST(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = '__all__'


class CollegesSerializerGET(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    def get_rating(self, college):
        rating = 0 if college.number_ratings == 0 else college.total_rating/college.number_ratings
        return rating

    class Meta:
        model = College
        fields = ('id', 'name', 'city', 'state', 'latitude', 'longitude', 'number_ratings', 'rating', 'city_id')
