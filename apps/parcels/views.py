from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse, inline_serializer
from core.responses.base import success, error
from apps.tracking.services import create_tracking_event
from apps.users.permissions import IsClient, IsCourier, IsAdmin
from .models import Parcel
from .serializers import ParcelSerializer
from apps.tracking.serializers import TrackingEventSerializer
from .services import assign_nearest_courier


# Serializer de confirmation générique pour les réponses message/courier (wrapper standard)
class AssignCourierResponseSerializer(serializers.Serializer):
    status = serializers.CharField(default="success")
    message = serializers.CharField()
    data = inline_serializer(
        name="AssignCourierData",
        fields={"courier": serializers.CharField(required=False, allow_null=True)}
    )


class ParcelCreateView(generics.CreateAPIView):
    """
    Crée un nouveau colis.

    Accessible uniquement aux clients authentifiés.
    Le code de tracking est généré automatiquement dans le serializer.
    """
    queryset = Parcel.objects.all()
    serializer_class = ParcelSerializer
    permission_classes = [IsAuthenticated, IsClient]

    @extend_schema(
        summary="Créer un nouveau colis",
        description="Crée un colis avec génération automatique du code de tracking. "
                    "Les coordonnées GPS du point de ramassage sont obligatoires.",
        tags=["Parcels"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ParcelListView(generics.ListAPIView):
    """
    Liste tous les colis envoyés par l'utilisateur connecté.

    Chaque client ne voit que ses propres colis (filtrés sur sender).
    """
    serializer_class = ParcelSerializer
    permission_classes = [IsAuthenticated, IsClient]

    @extend_schema(
        summary="Lister mes colis",
        description="Retourne tous les colis créés par le client connecté.",
        tags=["Parcels"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # Filtrer sur l'utilisateur courant — un client ne voit que ses colis
        return Parcel.objects.filter(sender=self.request.user)


class UpdateParcelStatusView(APIView):
    """
    Met à jour le statut d'un colis.

    Accessible uniquement aux livreurs authentifiés.
    La permission au niveau objet (IsAssignedCourier) est vérifiée explicitement
    pour s'assurer que seul le livreur assigné au colis peut modifier son statut.
    """
    permission_classes = [IsAuthenticated, IsCourier]

    @extend_schema(
        summary="Mettre à jour le statut d'un colis",
        description=(
            "Permet au livreur assigné de faire avancer le statut d'un colis. "
            "Statuts valides : `pending`, `assigned`, `picked`, `in_transit`, `delivered`."
        ),
        request={"application/json": {"type": "object", "properties": {
            "status": {"type": "string", "example": "in_transit"}
        }}},
        responses={200: ParcelSerializer},
        tags=["Parcels"],
    )
    def patch(self, request, parcel_id):
        status = request.data.get('status')

        try:
            parcel = Parcel.objects.get(id=parcel_id)
        except Parcel.DoesNotExist:
            return error(message="Parcel not found", status=404)

        # Déclenche la vérification has_object_permission sur les permissions enregistrées
        self.check_object_permissions(request, parcel)

        parcel.status = status
        parcel.save()

        # Créer un événement pour tracer ce changement de statut dans l'historique
        create_tracking_event(parcel, status, f"Parcel status updated to {status}")

        return success(
            message="Status updated",
            data={"parcel_id": str(parcel_id), "status": parcel.status}
        )


class ParcelTrackingView(APIView):
    """
    Retourne le statut et l'historique complet d'un colis via son code de tracking.

    Endpoint public — aucune authentification requise.
    Utilisé par les clients pour suivre leur livraison en temps réel.
    """

    @extend_schema(
        summary="Suivre un colis par son code de tracking",
        description=(
            "Endpoint public (sans authentification). "
            "Retourne le statut actuel et la timeline complète des événements d'un colis "
            "identifié par son code de tracking (ex: TG482910)."
        ),
        parameters=[
            OpenApiParameter(
                name="code",
                location=OpenApiParameter.PATH,
                description="Code de tracking du colis (ex: TG482910)",
                required=True,
                type=OpenApiTypes.STR,
            )
        ],
        responses={
            200: TrackingEventSerializer(many=True),
            404: {"description": "Colis introuvable"},
        },
        tags=["Parcels"],
    )
    def get(self, request, code):
        try:
            parcel = Parcel.objects.get(tracking_code=code)
        except Parcel.DoesNotExist:
            return error(message="Parcel not found", status=404)

        # Récupérer les événements triés du plus ancien au plus récent
        events = parcel.events.all().order_by("created_at")
        serializer = TrackingEventSerializer(events, many=True)

        return success(
            data={
                "tracking_code": parcel.tracking_code,
                "status": parcel.status,
                "events": serializer.data
            }
        )


class AssignCourierView(APIView):
    """
    Déclenche l'algorithme d'assignation automatique du livreur le plus proche.

    Accessible uniquement aux administrateurs.
    Si aucun livreur n'est disponible, retourne un message informatif sans erreur.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    # Indique à drf-spectacular quel serializer utiliser pour la réponse
    serializer_class = AssignCourierResponseSerializer

    @extend_schema(
        summary="Assigner automatiquement un livreur à un colis",
        description=(
            "Déclenche l'algorithme de recherche du livreur disponible le plus proche "
            "du point de ramassage du colis. "
            "Le livreur est marqué comme indisponible après assignation."
        ),
        responses={
            200: AssignCourierResponseSerializer,
            404: OpenApiResponse(description="Colis introuvable"),
        },
        tags=["Parcels"],
    )
    def post(self, request, parcel_id):
        try:
            parcel = Parcel.objects.get(id=parcel_id)
        except Parcel.DoesNotExist:
            return error(message="Parcel not found", status=404)

        # Lancer la recherche du livreur disponible le plus proche
        courier = assign_nearest_courier(parcel)

        if not courier:
            return success(message="No courier available")

        return success(
            message="Courier assigned",
            data={"courier": courier.user.username}
        )
