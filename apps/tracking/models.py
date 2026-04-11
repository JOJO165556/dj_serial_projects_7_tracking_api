from django.db import models
from apps.parcels.models import Parcel
from django.utils.translation import gettext_lazy as _

class TrackingEvent(models.Model):
    EVENT_TYPES = [
        ('created', _('Created')),
        ('assigned', _('Assigned')),
        ("picked", _("Picked up")),
        ("in_transit", _("In transit")),
        ('delivered', _("Delivered")),
    ]

    parcel = models.ForeignKey(
        Parcel,
        on_delete=models.CASCADE,
        related_name='events'
    )

    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parcel.tracking_code} - {self.event_type}"