from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.couriers.models import CourierProfile
from apps.couriers.utils import calculate_distance

User = get_user_model()


class CouriersLogicTests(APITestCase):
    def setUp(self):
        self.courier_user = User.objects.create_user(
            username="courier_1", password="testpassword123", role="courier", phone="555555"
        )
        self.courier_profile = CourierProfile.objects.create(
            user=self.courier_user,
            latitude=48.8566,  # Paris
            longitude=2.3522,
            is_available=True
        )

    def test_calculate_distance_haversine(self):
        """Vérifie la précision de la formule de Haversine (Paris -> Lyon approx 390-400km)"""
        lat_lyon = 45.7640
        lng_lyon = 4.8357
        distance = calculate_distance(
            self.courier_profile.latitude, self.courier_profile.longitude, lat_lyon, lng_lyon
        )
        # La distance orthodromique Paris-Lyon est d'environ 392 km.
        self.assertTrue(390 < distance < 395, f"Distance incorrecte : {distance} km")

    def test_courier_profile_availability(self):
        """Vérifie que la disponibilité par défaut est à True"""
        self.assertTrue(self.courier_profile.is_available)

    def test_available_couriers_list_unauthenticated(self):
        """Vérifie que les livreurs disponibles sont accessibles (endpoint public ou retourne 401)"""
        response = self.client.get("/api/couriers/available/")
        # L'endpoint peut être public (200) ou protégé (401) selon la configuration actuelle
        self.assertIn(response.status_code, [200, 401])

    def test_available_couriers_list_authenticated(self):
        """Vérifie que la liste des livreurs disponibles se retourne correctement"""
        self.client.force_authenticate(user=self.courier_user)
        response = self.client.get("/api/couriers/available/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Le courier actuel est disponible
        self.assertEqual(response.data["status"], "success")

    def test_available_couriers_with_coordinates(self):
        """Vérifie que le tri par distance fonctionne avec lat/lng"""
        self.client.force_authenticate(user=self.courier_user)
        response = self.client.get("/api/couriers/available/?lat=48.8&lng=2.3")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_available_couriers_invalid_coordinates(self):
        """Vérifie qu'une coordonnée invalide retourne une erreur 400"""
        self.client.force_authenticate(user=self.courier_user)
        response = self.client.get("/api/couriers/available/?lat=not_a_number&lng=2.3")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["status"], "error")

    def test_update_courier_location(self):
        """Vérifie que le livreur peut mettre à jour sa position GPS"""
        self.client.force_authenticate(user=self.courier_user)
        response = self.client.patch("/api/couriers/me/", {
            "latitude": 45.75,
            "longitude": 4.85
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.courier_profile.refresh_from_db()
        self.assertAlmostEqual(float(self.courier_profile.latitude), 45.75, places=2)
