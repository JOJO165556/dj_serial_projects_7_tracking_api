from datetime import timedelta
from django.utils import timezone
from apps.parcels.models import Parcel
from apps.tracking.models import TrackingEvent
from apps.couriers.models import CourierProfile


def parcel_kpis():
    """
    Calcule les indicateurs clés de performance (KPI) liés aux colis.

    Retourne un dictionnaire contenant :
    - total                   : nombre total de colis
    - delivered               : nombre de colis livrés
    - pending                 : nombre de colis en attente d'assignation
    - avg_delivery_time_seconds : temps moyen de livraison en secondes
                                  (entre la création et l'événement 'delivered')
    """
    parcels = Parcel.objects.all()

    # Filtrer les colis par statut pour les compteurs
    delivered = parcels.filter(status='delivered')
    pending = parcels.filter(status='pending')

    avg_time = 0

    # Calculer le temps moyen uniquement s'il y a des colis livrés
    if delivered.exists():
        total_seconds = 0
        count = 0

        for parcel in delivered:
            created = parcel.created_at
            # Récupérer l'événement 'delivered' pour obtenir la date de livraison réelle
            delivered_event = parcel.events.filter(event_type='delivered').first()

            if delivered_event:
                delta = delivered_event.created_at - created
                total_seconds += delta.total_seconds()
                count += 1

        # Eviter la division par zéro si aucun événement 'delivered' n'est trouvé
        avg_time = total_seconds / count if count > 0 else 0

    return {
        "total": parcels.count(),
        "delivered": delivered.count(),
        "pending": pending.count(),
        "avg_delivery_time_seconds": avg_time,
    }


def courier_kpis():
    """
    Calcule les indicateurs clés de performance liés aux livreurs.

    Retourne un dictionnaire contenant :
    - total     : nombre total de livreurs enregistrés
    - available : nombre de livreurs actuellement disponibles
    - busy      : nombre de livreurs en cours de livraison (non disponibles)
    """
    couriers = CourierProfile.objects.all()

    return {
        "total": couriers.count(),
        "available": couriers.filter(is_available=True).count(),
        "busy": couriers.filter(is_available=False).count(),
    }


def system_kpis():
    """
    Calcule les indicateurs d'activité système sur les dernières 24 heures.

    Retourne un dictionnaire contenant :
    - event_last_24h      : nombre total d'événements de tracking créés dans les 24 dernières heures
    - deliveries_last_24h : nombre de livraisons confirmées dans les 24 dernières heures
    """
    # Calculer le seuil temporel : maintenant moins 24 heures
    last_24h = timezone.now() - timedelta(hours=24)

    # Filtrer les événements récents pour les compteurs d'activité
    recent_events = TrackingEvent.objects.filter(
        created_at__gte=last_24h
    )

    return {
        "event_last_24h": recent_events.count(),
        "deliveries_last_24h": recent_events.filter(event_type='delivered').count(),
    }
