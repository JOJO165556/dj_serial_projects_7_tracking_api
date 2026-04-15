from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.parcels.models import Parcel
from apps.couriers.models import CourierProfile

User = get_user_model()

class ParcelAPITests(APITestCase):
    def setUp(self):
        # Création Admin
        self.admin_user = User.objects.create_user(
            username="admin1", password="password123", role="admin", phone="123"
        )
        
        # Création Client 1 et Client 2 pour tester le cloisonnement
        self.client_1 = User.objects.create_user(
            username="client_1", password="password123", role="client", phone="1000"
        )
        self.client_2 = User.objects.create_user(
            username="client_2", password="password123", role="client", phone="2000"
        )

        # Création Livreur disponible
        self.courier_user = User.objects.create_user(
            username="courier_1", password="password123", role="courier", phone="3000"
        )
        self.courier_profile = CourierProfile.objects.create(
            user=self.courier_user,
            latitude=10.0,
            longitude=10.0,
            is_available=True
        )

        # Colis existant pour Client 1
        self.parcel = Parcel.objects.create(
            sender=self.client_1,
            receiver_name="Destinataire 1",
            receiver_phone="9999",
            pickup_address="Point A",
            delivery_address="Point B",
            pickup_lat=10.5,
            pickup_lng=10.5,
            status="pending"
        )

    def test_parcel_creation_by_client(self):
        """Valide qu'un client authentifié peut créer un colis (le sender étant injecté en HiddenField)"""
        self.client.force_authenticate(user=self.client_1)
        
        # En l'absence de noms de vue (name=..), on simule l'appel directement sur le bon endpoint s'il existe.
        # Dans tracking_api, Parcels sont via apps.parcels.urls
        # On peut appeler l'API directement si l'URL est connue, ou tester les services internes.
        # Faisons un test avec l'URL manuelle '/api/parcels/create/' en admettant ce path.
        response = self.client.post("/api/parcels/create/", {
            "receiver_name": "New Receiver",
            "receiver_phone": "12345",
            "pickup_address": "C",
            "delivery_address": "D",
            "pickup_lat": 2.0,
            "pickup_lng": 2.0
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Parcel.objects.count(), 2)
        created_parcel = Parcel.objects.get(receiver_name="New Receiver")
        self.assertEqual(created_parcel.sender, self.client_1)
        self.assertEqual(created_parcel.status, "pending")
        self.assertIsNotNone(created_parcel.tracking_code)

    def test_parcel_list_isolation(self):
        """Vérifie que Client 1 ne voit que ses propres colis"""
        self.client.force_authenticate(user=self.client_2)
        response = self.client.get("/api/parcels/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Client 2 ne possède aucun colis
        self.assertEqual(len(response.data), 0)

        self.client.force_authenticate(user=self.client_1)
        response = self.client.get("/api/parcels/")
        self.assertEqual(len(response.data), 1)

    def test_assign_courier_by_admin(self):
        """Vérifie le fonctionnement de l'assignation automatique par un administrateur"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Le livreur est aux coordonnées (10.0, 10.0), le colis à (10.5, 10.5).
        response = self.client.post(f"/api/parcels/assign/{self.parcel.id}/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Validation du succès uniforme
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Courier assigned")
        
        self.parcel.refresh_from_db()
        self.assertEqual(self.parcel.status, "assigned")
        self.assertEqual(self.parcel.assigned_courier, self.courier_profile)
        
        self.courier_profile.refresh_from_db()
        self.assertFalse(self.courier_profile.is_available, "Le livreur doit devenir indisponible")
