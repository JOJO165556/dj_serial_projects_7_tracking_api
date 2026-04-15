from django.db import models
from apps.parcels.models import Parcel
from django.utils.translation import gettext_lazy as _


class TrackingEvent(models.Model):
    """
    Représente un événement dans l'historique de suivi d'un colis.

    Chaque changement d'état d'un colis (création, assignation, ramassage, etc.)
    génère un TrackingEvent. L'ensemble de ces événements constitue la timeline
    de suivi visible par le client et le livreur.
    """

    # Types d'événements correspondant aux étapes du cycle de livraison
    EVENT_TYPES = [
        ('created', _('Created')),          # Colis créé par le client
        ('assigned', _('Assigned')),        # Livreur assigné automatiquement
        ("picked", _("Picked up")),         # Colis ramassé par le livreur
        ("in_transit", _("In transit")),    # En cours d'acheminement
        ('delivered', _("Delivered")),      # Livraison confirmée
    ]

    # Colis auquel cet événement est rattaché
    # related_name='events' permet d'accéder à l'historique via parcel.events.all()
    parcel = models.ForeignKey(
        Parcel,
        on_delete=models.CASCADE,
        related_name='events'
    )

    # Type de l'événement (doit correspondre à un choix de EVENT_TYPES)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)

    # Description textuelle optionnelle (ex: "Assigned to john_doe")
    description = models.TextField(blank=True)

    # Date et heure de création de l'événement (non modifiable)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parcel.tracking_code} - {self.event_type}"
