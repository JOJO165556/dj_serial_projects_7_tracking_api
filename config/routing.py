from django.urls import path
from apps.realtime import consumers

websocket_urlpatterns = [
    path("ws/tracking/<str:parcel_id>/", consumers.TrackingConsumer.as_asgi())
]