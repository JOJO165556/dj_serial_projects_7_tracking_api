import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from parcels.models import Parcel


class TrackingConsumer(AsyncWebsocketConsumer):
    """
    Consumer WebSocket pour le suivi temps réel d'un colis spécifique.

    Cycle de vie :
    1. connect()  — Authentifie l'utilisateur, vérifie l'accès au colis, rejoint le groupe ASGI.
    2. send_tracking_event() — Reçoit les mises à jour du Channel Layer et les envoie au client.
    3. disconnect() — Quitte le groupe ASGI à la fermeture de la connexion.

    Le groupe ASGI est nommé d'après le code de tracking : 'parcel_<tracking_code>'.
    Seuls le sender, le livreur assigné et les admins peuvent se connecter.
    """

    async def connect(self):
        """
        Gère la connexion WebSocket entrante.

        Ferme la connexion immédiatement si :
        - l'utilisateur n'est pas authentifié
        - l'utilisateur n'a pas accès au colis demandé
        """
        self.user = self.scope['user']

        # Refuser les connexions anonymes — le middleware JWT doit avoir authentifié l'utilisateur
        if self.user.is_anonymous:
            await self.close()
            return

        # Récupérer le code de tracking depuis l'URL de la route WebSocket
        self.parcel_code = self.scope['url_route']['kwargs']['parcel_code']

        # Vérifier en base que l'utilisateur a le droit de suivre ce colis
        allowed = await self.check_access()

        if not allowed:
            await self.close()
            return

        # Construire le nom du groupe ASGI pour ce colis
        self.group_name = f"parcel_{self.parcel_code}"

        # Rejoindre le groupe pour recevoir les mises à jour diffusées via le Channel Layer
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    @database_sync_to_async
    def check_access(self):
        """
        Vérifie que l'utilisateur a le droit d'accéder au suivi de ce colis.

        Retourne True si l'utilisateur est :
        - le client expéditeur du colis
        - le livreur assigné au colis
        - un administrateur

        Retourne False si le colis n'existe pas.
        """
        try:
            parcel = Parcel.objects.get(tracking_code=self.parcel_code)

            return (
                parcel.sender == self.user
                or parcel.assigned_courier.user == self.user
                or self.user.role == "admin"
            )
        except Parcel.DoesNotExist:
            return False

    async def disconnect(self, close_code):
        """
        Gère la déconnexion WebSocket.

        Retire le canal du groupe ASGI pour arrêter de recevoir les mises à jour.
        """
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_tracking_event(self, event):
        """
        Reçoit un événement du Channel Layer et l'envoie au client WebSocket.

        Appelé automatiquement par le Channel Layer quand un message de type
        'send_tracking_event' est diffusé sur le groupe de ce colis.
        """
        await self.send(text_data=json.dumps({
            "type": "tracking_update",
            "data": event["data"]
        }))
