from rest_framework import serializers
from .models import TrackingEvent


class TrackingEventSerializer(serializers.ModelSerializer):
    """
    Serializer en lecture seule pour les événements de tracking.

    Expose uniquement les informations nécessaires à l'affichage de la timeline
    de suivi d'un colis : type de l'événement, description et horodatage.
    """
    class Meta:
        model = TrackingEvent
        fields = ["event_type", "description", "created_at"]