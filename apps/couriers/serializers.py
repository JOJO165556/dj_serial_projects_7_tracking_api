from rest_framework import serializers
from .models import CourierProfile


class CourierSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourierProfile
        fields = [
            "id",
            "user",
            "latitude",
            "longitude",
            "is_available",
        ]
        read_only_fields = ["user"]


class CourierLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourierProfile
        fields = ["latitude", "longitude"]
