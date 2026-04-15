from channels.generic.websocket import AsyncWebsocketConsumer
import json


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer WebSocket pour les notifications temps réel d'un utilisateur.

    Chaque utilisateur connecté rejoint un groupe ASGI dédié nommé 'user_<id>'.
    Quand une notification lui est envoyée via le service, elle est diffusée
    sur ce groupe et reçue en temps réel par ce consumer.

    La connexion est refusée si l'utilisateur n'est pas authentifié.
    """

    async def connect(self):
        """
        Gère la connexion WebSocket.

        Ferme la connexion immédiatement si l'utilisateur est anonyme.
        Sinon, rejoint le groupe de notifications personnel de l'utilisateur.
        """
        self.user = self.scope['user']

        # Refuser la connexion si l'utilisateur n'est pas authentifié
        if self.user.is_anonymous:
            await self.close()
            return

        # Le groupe est unique par utilisateur, basé sur son ID
        self.group_name = f"user_{self.user.id}"

        # Rejoindre le groupe pour recevoir les notifications de cet utilisateur
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """
        Gère la déconnexion WebSocket.

        Retire le canal du groupe pour éviter d'envoyer des messages à un client déconnecté.
        """
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        """
        Reçoit une notification du Channel Layer et l'envoie au client WebSocket.

        Appelé automatiquement quand un message de type 'send_notification' est
        diffusé sur le groupe de cet utilisateur.
        """
        await self.send(text_data=json.dumps({
            "type": "notification",
            "data": event["data"]
        }))
