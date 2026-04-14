from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_tracking_update(parcel, event_data):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"parcel_{parcel.tracking_code}",
        {
            "type": "send_tracking_update",
            "data": event_data
        }
    )