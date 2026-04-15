from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from apps.realtime.middleware import JWTWebSocketAuthMiddleware
from apps.realtime.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTWebSocketAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})
