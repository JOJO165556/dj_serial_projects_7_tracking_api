import random
import string
from rest_framework import serializers

from tracking.services import create_tracking_event
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
            "pickup_lat",
            "pickup_lng",
            "status",
            "assigned_courier",
            "created_at",
        ]
        read_only_fields = ["tracking_code", "status", "assigned_courier"]

    #Pour garantir l'unicité
    def create(self, validated_data):
        while True:
            code = generate_tracking_code()
            if not Parcel.objects.filter(tracking_code=code).exists():
                break

        validated_data["tracking_code"] = code
        parcel = super().create(validated_data)

        create_tracking_event(parcel, "created", "Parcel created")

        return parcel

    def validate(self, data):
        if data.get("pickup_lat") is None or data.get("pickup_lng") is None:
            raise serializers.ValidationError("Pickup location required")
        return data