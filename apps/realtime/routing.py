from django.urls import re_path
from apps.realtime.consumers import TrackingConsumer
from apps.notifications.consumers import NotificationConsumer  

websocket_urlpatterns = [
    re_path(r"ws/tracking/(?P<parcel_code>\w+)/$", TrackingConsumer.as_asgi()),
    re_path(r"ws/notifications/$", NotificationConsumer.as_asgi()),
]
