from django.db import models
from django.conf import settings
import uuid
from django.utils.translation import gettext_lazy as _

# Référence au modèle User configuré dans les settings (AUTH_USER_MODEL)
User = settings.AUTH_USER_MODEL


class Parcel(models.Model):
    """
    Représente un colis en cours de livraison.

    Un colis est créé par un client (sender), possède un code de suivi unique,
    des adresses de ramassage et de livraison, et peut être assigné à un livreur.
    Son statut évolue au fil du cycle de livraison.
    """

    # Cycle de vie possible pour un colis
    STATUS_CHOICES = [
        ('pending', _('Pending')),          # En attente d'assignation
        ('assigned', _('Assigned')),        # Assigné à un livreur
        ("picked", _("Picked Up")),         # Ramassé par le livreur
        ("in_transit", _("In transit")),    # En cours de livraison
        ('delivered', _("Delivered")),      # Livré au destinataire
    ]

    # Identifiant unique non séquentiel (UUID v4) pour éviter l'énumération
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # L'utilisateur qui a créé et envoyé le colis
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_parcels',
    )

    # Informations sur le destinataire
    receiver_name = models.CharField(max_length=120)
    receiver_phone = models.CharField(max_length=20)

    # Adresses textuelles de ramassage et de livraison
    pickup_address = models.CharField(max_length=255)
    delivery_address = models.CharField(max_length=255)

    # Statut courant du colis dans le cycle de livraison
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Livreur assigné au colis — pointe vers CourierProfile pour accéder aux coords GPS
    assigned_courier = models.ForeignKey(
        "couriers.CourierProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries'
    )

    # Code alphanumérique unique utilisé pour le suivi public (ex: TG123456)
    tracking_code = models.CharField(max_length=20, unique=True)

    # Coordonnées GPS du point de ramassage (utilisées pour l'assignation automatique)
    pickup_lat = models.FloatField(null=True, blank=True)
    pickup_lng = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tracking_code} - {self.status}"