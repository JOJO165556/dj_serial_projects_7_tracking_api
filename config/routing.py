from django.urls import re_path
from apps.realtime.consumers import TrackingConsumer
from notifications.consumers import NotificationConsumer

websocket_urlpatterns = [
    re_path(r"ws/tracking/(?P<parcel_code>\w+)/$", TrackingConsumer.as_asgi()), # type: ignore
    re_path(r"ws/notifications/(?P<notification_id>\w+)/$", NotificationConsumer.as_asgi()), #try: ignore
]