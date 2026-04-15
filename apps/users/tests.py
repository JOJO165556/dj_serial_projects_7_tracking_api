from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationAndViewTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin_dash", password="password123", role="admin", phone="000"
        )

    def test_user_registration(self):
        """Vérifie qu'un utilisateur peut s'enregistrer avec les bonnes données"""
        response = self.client.post("/api/users/create/", {
            "username": "new_client",
            "password": "securepass123",
            "phone": "1234567890",
            "role": "client"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="new_client").exists())

    def test_user_registration_missing_field(self):
        """Vérifie que l'enregistrement échoue si un champ obligatoire manque"""
        response = self.client.post("/api/users/create/", {
            "username": "incomplete_user",
            # manque password, phone, role
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
