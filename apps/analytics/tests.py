from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.parcels.models import Parcel
from apps.tracking.models import TrackingEvent
from apps.analytics.services import parcel_kpis
from django.utils import timezone
from datetime import timedelta
import uuid

User = get_user_model()


class AnalyticsTests(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username="client_analytics", password="password123", role="client", phone="000"
        )

        # Colis livré
        self.parcel_delivered = Parcel.objects.create(
            id=uuid.uuid4(),
            sender=self.client_user,
            status="delivered",
            tracking_code="TG111111"
        )
        # On simule l'historique
        TrackingEvent.objects.create(parcel=self.parcel_delivered, event_type="created",
                                     created_at=timezone.now() - timedelta(hours=2))
        TrackingEvent.objects.create(parcel=self.parcel_delivered, event_type="delivered", created_at=timezone.now())

        # Colis en attente
        self.parcel_pending = Parcel.objects.create(
            id=uuid.uuid4(),
            sender=self.client_user,
            status="pending",
            tracking_code="TG222222"
        )

    def test_parcel_kpis_calculation(self):
        """Valide les agrégations de KPIs liées aux colis"""
        kpis = parcel_kpis()

        self.assertEqual(kpis["total"], 2)
        self.assertEqual(kpis["delivered"], 1)
        self.assertEqual(kpis["pending"], 1)

        # Le temps de livraison doit avoir été capturé proprement
        self.assertTrue(kpis["avg_delivery_time_seconds"] > 0)
