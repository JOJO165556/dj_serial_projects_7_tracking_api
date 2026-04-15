from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.parcels.models import Parcel
from apps.couriers.models import CourierProfile

User = get_user_model()


class AdminDashboardTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin_dash", password="password123", role="admin", phone="000"
        )
        self.client_user = User.objects.create_user(
            username="client_dash", password="password123", role="client", phone="111"
        )
        self.courier_user = User.objects.create_user(
            username="courier_dash", password="password123", role="courier", phone="222"
        )
        CourierProfile.objects.create(user=self.courier_user, is_available=True)
        Parcel.objects.create(
            sender=self.client_user,
            status="pending",
            tracking_code="TG000001"
        )

    def test_dashboard_accessible_by_admin(self):
        """Vérifie que l'admin peut accéder au tableau de bord"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/dashboard/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        self.assertIn("parcels", response.data["data"])
        self.assertIn("couriers", response.data["data"])

    def test_dashboard_blocked_for_non_admin(self):
        """Vérifie qu'un client ne peut pas accéder au tableau de bord"""
        self.client.force_authenticate(user=self.client_user)
        response = self.client.get("/api/dashboard/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_dashboard_requires_authentication(self):
        """Vérifie que le dashboard redéfinit l'accès (403 sans credentials JWT)"""
        response = self.client.get("/api/dashboard/")
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
