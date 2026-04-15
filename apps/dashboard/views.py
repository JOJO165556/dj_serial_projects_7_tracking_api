from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers

from core.responses.base import success
from apps.parcels.models import Parcel
from apps.couriers.models import CourierProfile
from apps.users.permissions import IsAdmin


# Schéma inline décrivant la structure de la réponse standardisée pour Swagger
_dashboard_response_schema = inline_serializer(
    name="DashboardResponse",
    fields={
        "status": serializers.CharField(default="success"),
        "message": serializers.CharField(default="Dashboard data retrieved successfully"),
        "data": inline_serializer(
            name="DashboardData",
            fields={
                "parcels": inline_serializer(
                    name="DashboardParcelStats",
                    fields={
                        "total": serializers.IntegerField(),
                        "pending": serializers.IntegerField(),
                        "assigned": serializers.IntegerField(),
                        "in_transit": serializers.IntegerField(),
                        "delivered": serializers.IntegerField(),
                    }
                ),
                "couriers": inline_serializer(
                    name="DashboardCourierStats",
                    fields={
                        "total": serializers.IntegerField(),
                        "available": serializers.IntegerField(),
                        "busy": serializers.IntegerField(),
                    }
                ),
            }
        )
    }
)


class AdminDashboardView(APIView):
    """
    Vue de tableau de bord réservée aux administrateurs.

    Fournit un aperçu rapide de l'ensemble des colis (répartis par statut)
    et des livreurs (disponibles vs occupés) en un seul appel.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        summary="Tableau de bord administrateur",
        description=(
            "Retourne un résumé de l'activité de la plateforme :\n"
            "- **parcels** : compteurs par statut (pending, assigned, in_transit, delivered)\n"
            "- **couriers** : total, disponibles, occupés"
        ),
        responses={200: _dashboard_response_schema},
        tags=["Dashboard"],
    )
    def get(self, request):
        parcels = Parcel.objects.all()
        couriers = CourierProfile.objects.all()

        data = {
            "parcels": {
                "total": parcels.count(),
                "pending": parcels.filter(status="pending").count(),
                "assigned": parcels.filter(status="assigned").count(),
                "in_transit": parcels.filter(status="in_transit").count(),
                "delivered": parcels.filter(status="delivered").count(),
            },
            "couriers": {
                "total": couriers.count(),
                "available": couriers.filter(is_available=True).count(),
                "busy": couriers.filter(is_available=False).count(),
            }
        }

        return success(message="Dashboard data retrieved successfully", data=data)
