from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Notification


def send_realtime_notification(user, title, message):
    """
    Crée une notification en base de données et la diffuse en temps réel via WebSocket.

    Enregistre d'abord la notification en base pour la persistance,
    puis envoie une trame au groupe ASGI de l'utilisateur pour que
    le NotificationConsumer la transmette au client connecté.

    Paramètres :
    - user    : instance du modèle User destinataire de la notification
    - title   : titre court de la notification
    - message : corps du message de la notification

    Retourne l'instance Notification créée.
    """
    # Persister la notification en base pour la retrouver plus tard via l'API REST
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message
    )

    channel_layer = get_channel_layer()

    # Diffuser la notification en temps réel sur le groupe WebSocket de l'utilisateur
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",              # Groupe ciblé : unique par utilisateur
        {
            "type": "send_notification",  # Méthode à appeler sur le NotificationConsumer
            "data": {
                "title": title,
                "message": message,
                "created_at": str(notification.created_at)
            }
        }
    )

    return notification
