from apps.realtime.services import send_tracking_update
from .models import TrackingEvent


def create_tracking_event(parcel, event_type, description=""):
    """
    Crée un événement de tracking en base de données et déclenche la mise à jour temps réel.

    C'est le point d'entrée unique pour tracer un changement d'état d'un colis.
    Après création de l'événement, la mise à jour est diffusée via le Channel Layer
    pour notifier en temps réel tous les clients WebSocket abonnés à ce colis.

    Paramètres :
    - parcel      : instance du modèle Parcel concerné
    - event_type  : type de l'événement (doit correspondre à TrackingEvent.EVENT_TYPES)
    - description : texte libre décrivant l'événement (optionnel)

    Retourne l'instance TrackingEvent créée.
    """
    # Persister l'événement dans l'historique de suivi du colis
    event = TrackingEvent.objects.create(
        parcel=parcel,
        event_type=event_type,
        description=description
    )

    # Diffuser la mise à jour aux clients WebSocket connectés à ce colis
    send_tracking_update(parcel, {
        "event_type": event.event_type,
        "description": event.description,
        "timestamp": str(event.created_at)
    })

    return event
