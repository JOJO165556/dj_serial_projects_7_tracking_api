import random
import string
from rest_framework import serializers

from apps.tracking.services import create_tracking_event
from .models import Parcel


def generate_tracking_code():
    """
    Génère un code de tracking aléatoire au format 'TG' suivi de 6 chiffres.

    Ex: TG482910. L'unicité n'est pas garantie ici — elle est vérifiée dans create().
    """
    return "TG" + "".join(random.choices(string.digits, k=6))


class ParcelSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création et la lecture d'un colis.

    Le champ sender est automatiquement rempli avec l'utilisateur connecté
    (HiddenField) et n'est donc pas exposé dans les entrées de l'API.
    Les champs tracking_code, status et assigned_courier sont en lecture seule.
    """
    # Injecte automatiquement l'utilisateur authentifié comme expéditeur
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
        # Ces champs sont gérés par le système et ne doivent pas être fournis par le client
        read_only_fields = ["tracking_code", "status", "assigned_courier"]

    def create(self, validated_data):
        """
        Crée un colis avec un code de tracking unique.

        Génère un code aléatoire et relance la génération en boucle
        tant que le code existe déjà en base (collision rare mais possible).
        Crée également le premier événement de tracking 'created'.
        """
        # Boucle jusqu'à obtenir un code de tracking non encore utilisé
        while True:
            code = generate_tracking_code()
            if not Parcel.objects.filter(tracking_code=code).exists():
                break

        validated_data["tracking_code"] = code
        parcel = super().create(validated_data)

        # Enregistrer l'événement initial dans l'historique de suivi
        create_tracking_event(parcel, "created", "Parcel created")

        return parcel

    def validate(self, data):
        """
        Valide que les coordonnées GPS du point de ramassage sont présentes.

        Elles sont nécessaires pour l'algorithme d'assignation du livreur le plus proche.
        """
        if data.get("pickup_lat") is None or data.get("pickup_lng") is None:
            raise serializers.ValidationError("Pickup location required")
        return data
