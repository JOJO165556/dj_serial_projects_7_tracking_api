from django.urls import re_path
from apps.realtime.consumers import TrackingConsumer

websocket_urlpatterns = [
    re_path(r"ws/tracking/(?P<parcel_code>\w+)/$", TrackingConsumer.as_asgi()), # type: ignore
]