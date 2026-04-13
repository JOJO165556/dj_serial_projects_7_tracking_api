from apps.couriers.models import CourierProfile
from apps.couriers.utils import calculate_distance

#Assignation auto au livreur le plus proche
def assign_nearest_courier(parcel):
    couriers = CourierProfile.objects.filter(is_available=True)

    if not couriers.exists():
        return None

    best_courier = None
    min_distance = float("inf")

    for courier in couriers:
        if courier.latitude is None or courier.longitude is None:
            continue

        distance = calculate_distance(
            parcel.pickup_lat,
            parcel.pickup_lng,
            courier.latitude,
            courier.longitude,
        )

        if distance < min_distance:
            min_distance = distance
            best_courier = courier

    if best_courier:
        parcel.assigned_courier = best_courier
        parcel.status = "assigned"
        parcel.save()

        best_courier.is_available = False
        best_courier.save()

    return best_courier