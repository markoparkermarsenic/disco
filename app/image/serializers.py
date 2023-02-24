from django.contrib.auth.models import User
from image.models import Plan, Subscriber
from rest_framework import serializers


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ("name", "thumbnail_sizes", "expiring_links", "original_image")


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]


class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = ("user", "plan")
