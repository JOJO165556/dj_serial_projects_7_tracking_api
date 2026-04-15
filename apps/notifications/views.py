from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from core.responses.base import success
from .models import Notification


# Serializer simple pour les réponses de confirmation (message unique)
class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


# Schéma inline pour décrire la structure d'une notification dans Swagger (via le wrapper standard)
_notification_list_schema = inline_serializer(
    name="NotificationListResponse",
    fields={
        "status": serializers.CharField(default="success"),
        "message": serializers.CharField(default="Notifications retrieved successfully"),
        "data": inline_serializer(
            name="NotificationItem",
            many=True,
            fields={
                "id": serializers.IntegerField(),
                "title": serializers.CharField(),
                "message": serializers.CharField(),
                "is_read": serializers.BooleanField(),
                "created_at": serializers.DateTimeField(),
            }
        )
    }
)


class NotificationListView(APIView):
    """
    Retourne la liste des notifications de l'utilisateur connecté.

    Les notifications sont triées de la plus récente à la plus ancienne.
    Chaque notification indique si elle a déjà été lue (is_read).
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Lister mes notifications",
        description="Retourne toutes les notifications de l'utilisateur connecté, "
                    "triées de la plus récente à la plus ancienne.",
        responses={200: _notification_list_schema},
        tags=["Notifications"],
    )
    def get(self, request):
        # Filtrer uniquement les notifications appartenant à l'utilisateur connecté
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

        return success(message="Notifications retrieved successfully", data=[
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "is_read": n.is_read,
                "created_at": n.created_at
            }
            for n in notifications
        ])


class MarkNotificationReadView(APIView):
    """
    Marque une notification spécifique comme lue.

    Accessible uniquement à l'utilisateur propriétaire de la notification.
    Utilise get_object_or_404 pour retourner automatiquement un 404
    si la notification n'existe pas ou n'appartient pas à l'utilisateur.
    """
    permission_classes = [IsAuthenticated]
    # Indique à drf-spectacular quel serializer utiliser pour la réponse
    serializer_class = MessageSerializer

    @extend_schema(
        summary="Marquer une notification comme lue",
        description="Met à jour le champ `is_read` à `true` pour la notification spécifiée. "
                    "Retourne un 404 si la notification n'appartient pas à l'utilisateur connecté.",
        responses={
            200: MessageSerializer,
            404: OpenApiResponse(description="Notification introuvable ou non autorisée"),
        },
        tags=["Notifications"],
    )
    def patch(self, request, notification_id):
        # Vérifier que la notification existe et appartient bien à l'utilisateur connecté
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return success(message="Notification marked as read")
