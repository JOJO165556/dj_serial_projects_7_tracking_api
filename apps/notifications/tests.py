from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from unittest.mock import patch
from apps.notifications.services import send_realtime_notification
from apps.notifications.models import Notification

User = get_user_model()


class NotificationsTests(APITestCase):
    def setUp(self):
        self.client_user = User.objects.create_user(
            username="client_notifications", password="password123", role="client", phone="12"
        )
        self.other_user = User.objects.create_user(
            username="other_client", password="password123", role="client", phone="99"
        )

    @patch("apps.notifications.services.async_to_sync")
    @patch("apps.notifications.services.get_channel_layer")
    def test_send_realtime_notification_creates_db_entry(self, mock_layer, mock_async):
        """Vérifie que l'envoi d'une notification l'inscrit en base de données"""
        notification = send_realtime_notification(
            user=self.client_user,
            title="Alerte",
            message="Ton colis approche !"
        )

        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(notification.title, "Alerte")
        self.assertFalse(notification.is_read)
        self.assertEqual(notification.user, self.client_user)

    def test_list_notifications_authenticated(self):
        """Vérifie que l'utilisateur voit ses propres notifications"""
        Notification.objects.create(
            user=self.client_user, title="Test", message="Message", is_read=False
        )
        Notification.objects.create(
            user=self.other_user, title="Autre", message="Autre message", is_read=False
        )

        self.client.force_authenticate(user=self.client_user)
        response = self.client.get("/api/notifications/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        # client_user ne voit que sa notification
        self.assertEqual(len(response.data["data"]), 1)

    def test_list_notifications_unauthenticated(self):
        """Vérifie que les notifications nécessitent un accès authentifié (403 sans credentials JWT)"""
        response = self.client.get("/api/notifications/")
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_mark_notification_as_read(self):
        """Vérifie que marquer une notification comme lue fonctionne"""
        notification = Notification.objects.create(
            user=self.client_user, title="Test", message="Message", is_read=False
        )

        self.client.force_authenticate(user=self.client_user)
        response = self.client.patch(f"/api/notifications/{notification.id}/read/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_mark_other_user_notification_returns_404(self):
        """Vérifie qu'on ne peut pas marquer la notification d'un autre utilisateur"""
        notification = Notification.objects.create(
            user=self.other_user, title="Test", message="Autre", is_read=False
        )

        self.client.force_authenticate(user=self.client_user)
        response = self.client.patch(f"/api/notifications/{notification.id}/read/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
