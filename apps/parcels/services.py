from apps.couriers.models import CourierProfile
from apps.couriers.utils import calculate_distance
from apps.tracking.services import create_tracking_event


def assign_nearest_courier(parcel):
    """
    Assigne automatiquement le livreur disponible le plus proche du point de ramassage.

    Parcourt tous les livreurs disponibles ayant des coordonnées GPS valides,
    calcule la distance par rapport aux coordonnées de ramassage du colis,
    et assigne celui dont la distance est minimale.

    Retourne le CourierProfile assigné, ou None si aucun livreur n'est disponible.
    """
    # Récupérer uniquement les livreurs marqués comme disponibles
    couriers = CourierProfile.objects.filter(is_available=True)

    if not couriers.exists():
        return None

    best_courier = None
    # Initialiser la distance minimale à l'infini pour garantir que tout livreur sera meilleur
    min_distance = float("inf")

    for courier in couriers:
        # Ignorer les livreurs sans position GPS enregistrée
        if courier.latitude is None or courier.longitude is None:
            continue

        distance = calculate_distance(
            parcel.pickup_lat,
            parcel.pickup_lng,
            courier.latitude,
            courier.longitude,
        )

        # Mettre à jour le meilleur candidat si ce livreur est plus proche
        if distance < min_distance:
            min_distance = distance
            best_courier = courier

    if best_courier:
        # Assigner le livreur au colis et passer le statut à "assigned"
        parcel.assigned_courier = best_courier
        parcel.status = "assigned"
        parcel.save()

        # Marquer le livreur comme indisponible pour éviter une double assignation
        best_courier.is_available = False
        best_courier.save()

        # Créer un événement de tracking pour tracer l'assignation
        create_tracking_event(
            parcel,
            "assigned",
            f"Assigned to {best_courier.user.username}"
        )

    return best_courier


def delivery_step(parcel, status, message):
    """
    Met à jour le statut d'un colis et crée l'événement de tracking correspondant.

    Utilisé à chaque étape du cycle de livraison (ex: picked, in_transit, delivered).
    """
    parcel.status = status
    parcel.save()
    # Enregistrer l'événement pour tenir à jour l'historique de suivi
    create_tracking_event(parcel, status, message)
