from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_tracking_update(parcel, event_data):
    """
    Diffuse une mise à jour de tracking à tous les clients WebSocket abonnés au colis.

    Utilise le Channel Layer (Redis ou InMemory selon la config) pour envoyer
    un message au groupe ASGI nommé 'parcel_<tracking_code>'.
    Le message est de type 'send_tracking_event', ce qui fait que le Channel Layer
    appellera automatiquement la méthode send_tracking_event() du consumer.

    Paramètres :
    - parcel     : instance du modèle Parcel concerné
    - event_data : dictionnaire contenant les données à envoyer (type, description, timestamp)
    """
    # Récupérer l'instance du Channel Layer configurée dans les settings
    channel_layer = get_channel_layer()

    # async_to_sync permet d'appeler une coroutine depuis du code synchrone (vue, service)
    async_to_sync(channel_layer.group_send)(
        f"parcel_{parcel.tracking_code}",   # Groupe ciblé par ce colis
        {
            "type": "send_tracking_event",  # Nom de la méthode à appeler sur le consumer
            "data": event_data
        }
    )
