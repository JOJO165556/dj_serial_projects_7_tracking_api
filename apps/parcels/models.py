from django.db import models
from django.conf import settings
import uuid
from django.utils.translation import gettext_lazy as _

User = settings.AUTH_USER_MODEL

#Parcel model
class Parcel(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('assigned', _('Assigned')),
        ("picked", _("Picked Up")),
        ("in_transit", _("In transit")),
        ('delivered', _("Delivered")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_parcels',
    )

    recruiter_name = models.CharField(max_length=120)
    receiver_phone = models.CharField(max_length=20)

    pickup_address = models.CharField(max_length=255)
    delivery_address = models.CharField(max_length=255)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    assigned_courier = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deliveries'
    )

    tracking_code = models.CharField(max_length=20, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tracking_code} - {self.status}"