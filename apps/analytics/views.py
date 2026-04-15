from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers

from core.responses.base import success
from apps.users.permissions import IsAdmin
from .services import parcel_kpis, courier_kpis, system_kpis


# Schéma inline décrivant la structure de la réponse standardisée pour Swagger
_analytics_response_schema = inline_serializer(
    name="AnalyticsResponse",
    fields={
        "status": serializers.CharField(default="success"),
        "message": serializers.CharField(default="Analytics data retrieved successfully"),
        "data": inline_serializer(
            name="AnalyticsData",
            fields={
                "parcels": inline_serializer(
                    name="ParcelKPIs",
                    fields={
                        "total": serializers.IntegerField(),
                        "delivered": serializers.IntegerField(),
                        "pending": serializers.IntegerField(),
                        "avg_delivery_time_seconds": serializers.FloatField(),
                    }
                ),
                "couriers": inline_serializer(
                    name="CourierKPIs",
                    fields={
                        "total": serializers.IntegerField(),
                        "available": serializers.IntegerField(),
                        "busy": serializers.IntegerField(),
                    }
                ),
                "system": inline_serializer(
                    name="SystemKPIs",
                    fields={
                        "event_last_24h": serializers.IntegerField(),
                        "deliveries_last_24h": serializers.IntegerField(),
                    }
                ),
            }
        )
    }
)


class AnalyticsView(APIView):
    """
    Retourne les indicateurs clés de performance (KPI) de la plateforme.

    Accessible uniquement aux administrateurs.
    Agrège les données des colis, des livreurs et de l'activité système.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        summary="KPIs globaux de la plateforme",
        description=(
            "Retourne les indicateurs de performance agrégés :\n"
            "- **parcels** : total, livrés, en attente, temps moyen de livraison\n"
            "- **couriers** : total, disponibles, occupés\n"
            "- **system** : événements et livraisons des 24 dernières heures"
        ),
        responses={200: _analytics_response_schema},
        tags=["Analytics"],
    )
    def get(self, request):
        return success(message="Analytics data retrieved successfully", data={
            "parcels": parcel_kpis(),
            "couriers": courier_kpis(),
            "system": system_kpis()
        })