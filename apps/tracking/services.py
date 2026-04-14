from realtime.services import send_tracking_update
from .models import TrackingEvent

def create_tracking_event(parcel, event_type, description=""):
    event = TrackingEvent.objects.create(
        parcel=parcel,
        event_type=event_type,
        description=description
    )

    send_tracking_update(parcel, {
        "event_type": event.event_type,
        "description": event.description,
        "timestamp": str(event.created_at)
    })

    return event