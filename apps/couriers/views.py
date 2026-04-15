from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse, inline_serializer
from rest_framework import serializers
from apps.users.permissions import IsCourier
from core.responses.base import success, error

from .models import CourierProfile
from .serializers import CourierSerializer, CourierLocationSerializer
from .utils import calculate_distance


class CourierUpdateLocationView(generics.UpdateAPIView):
    """
    Met à jour la position GPS du livreur connecté.

    Accessible uniquement aux livreurs authentifiés.
    Le profil est récupéré à partir de l'utilisateur connecté — un livreur
    ne peut mettre à jour que sa propre position.
    """
    serializer_class = CourierLocationSerializer
    permission_classes = [IsAuthenticated, IsCourier]

    @extend_schema(
        summary="Mettre à jour la position GPS du livreur",
        description="Permet au livreur connecté de mettre à jour ses coordonnées GPS actuelles. "
                    "Ces coordonnées sont utilisées pour l'algorithme d'assignation automatique.",
        tags=["Couriers"],
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @extend_schema(
        summary="Remplacer la position GPS du livreur",
        description="Remplacement complet des coordonnées GPS du livreur connecté.",
        tags=["Couriers"],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def get_object(self):
        """
        Retourne le CourierProfile de l'utilisateur connecté.

        Lève une PermissionDenied si le rôle n'est pas 'courier',
        et NotFound si aucun profil n'est associé à cet utilisateur.
        """
        user = self.request.user

        # Double vérification du rôle (la permission de classe vérifie déjà cela,
        # mais cette garde protège aussi contre les appels directs à get_object)
        if user.role != "courier":
            raise PermissionDenied("Only couriers can update location")
        try:
            return CourierProfile.objects.get(user=user)
        except CourierProfile.DoesNotExist:
            raise NotFound("Courier profile not found")


class AvailableCouriersView(APIView):
    """
    Retourne la liste des livreurs disponibles, avec leur distance si des coordonnées sont fournies.

    Paramètres optionnels en query string :
    - lat : latitude du point de référence
    - lng : longitude du point de référence

    Si lat et lng sont fournis, les livreurs sont triés du plus proche au plus loin.
    """

    @extend_schema(
        summary="Lister les livreurs disponibles",
        description=(
            "Retourne tous les livreurs dont le statut est 'disponible'. "
            "Si les paramètres `lat` et `lng` sont fournis, la distance de chaque livreur "
            "par rapport au point de référence est calculée (formule Haversine) "
            "et les résultats sont triés du plus proche au plus loin."
        ),
        parameters=[
            OpenApiParameter(
                name="lat",
                location=OpenApiParameter.QUERY,
                description="Latitude du point de référence (ex: 48.8566)",
                required=False,
                type=OpenApiTypes.FLOAT,
            ),
            OpenApiParameter(
                name="lng",
                location=OpenApiParameter.QUERY,
                description="Longitude du point de référence (ex: 2.3522)",
                required=False,
                type=OpenApiTypes.FLOAT,
            ),
        ],
        responses={
            200: inline_serializer(
                name="AvailableCouriersResponse",
                fields={
                    "status": serializers.CharField(default="success"),
                    "message": serializers.CharField(default="Available couriers retrieved successfully"),
                    "data": CourierSerializer(many=True),
                }
            ),
            400: OpenApiResponse(description="Coordonnées invalides"),
        },
        tags=["Couriers"],
    )
    def get(self, request):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")

        # Convertir les paramètres en float si présents — retourner une erreur si invalides
        try:
            lat = float(lat) if lat else None
            lng = float(lng) if lng else None
        except ValueError:
            return error(message="Invalid coordinates", status=400)

        # Filtrer uniquement les livreurs marqués comme disponibles
        couriers = CourierProfile.objects.filter(is_available=True)
        result = []

        for c in couriers:
            # Ignorer les livreurs dont la position GPS n'est pas encore enregistrée
            if c.latitude is None or c.longitude is None:
                continue

            distance = None

            # Calculer la distance par rapport au point de référence si fourni
            if lat is not None and lng is not None:
                distance = calculate_distance(
                    lat,
                    lng,
                    c.latitude,
                    c.longitude
                )

            result.append({
                "id": c.id,
                "user": c.user.username,
                "lat": c.latitude,
                "lng": c.longitude,
                "distance": distance
            })

        # Trier les résultats par distance croissante si un point de référence a été fourni
        if lat is not None and lng is not None:
            result.sort(key=lambda x: x["distance"] if x["distance"] is not None else 9999)

        return success(message="Available couriers retrieved successfully", data=result)
