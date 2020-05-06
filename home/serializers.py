from django.contrib.auth.models import User
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer
from .models import Profile, UserPhoneDetail, UserActivation


class UserActivationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivation
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('college', 'degree', 'passing_year', 'number_reviews', 'id',)


class UserPhoneDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPhoneDetail
        fields = '__all__'
