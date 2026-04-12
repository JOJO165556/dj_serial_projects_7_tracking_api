import random
import string
from rest_framework import serializers
from .models import Parcel

def generate_tracking_code():
    return "TG" + "".join(random.choices(string.digits, k=6))

class ParcelSerializer(serializers.ModelSerializer):
    sender = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Parcel
        fields = [
            "id",
            "tracking_code",
            "sender",
            "receiver_name",
            "receiver_phone",
            "pickup_address",
            "delivery_address",
            "status",
            "assigned_courier",
            "created_at",
        ]
        read_only_fields = ["tracking_code", "status", "assigned_courier"]

    def create(self, validated_data):
        validated_data["tracking_code"] = generate_tracking_code()
        return super().create(validated_data)