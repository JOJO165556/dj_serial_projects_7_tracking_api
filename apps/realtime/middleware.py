from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTWebSocketAuthMiddleware:
    """
    Middleware ASGI d'authentification JWT pour les connexions WebSocket.

    Les WebSockets ne transmettent pas les cookies ou les en-têtes HTTP classiques
    de la même façon que les requêtes HTTP. Ce middleware intercepte le token JWT
    fourni dans l'en-tête Authorization (format : 'Bearer <token>') et injecte
    l'utilisateur correspondant dans le scope ASGI.

    Si le token est absent ou invalide, l'utilisateur reste AnonymousUser —
    c'est au consumer de décider quoi faire (accepter ou fermer la connexion).
    """

    def __init__(self, app):
        # Stocker la prochaine application ASGI dans la chaîne de middlewares
        self.app = app

    async def __call__(self, scope, receive, send):
        # Convertir les headers ASGI (liste de tuples bytes) en dictionnaire pour accès rapide
        headers = dict(scope["headers"])

        token = None

        # Chercher l'en-tête Authorization dans les headers (clés en bytes minuscules)
        if b"authorization" in headers:
            auth_header = headers[b"authorization"].decode()

            # Extraire le token brut après le préfixe "Bearer "
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        # Par défaut, l'utilisateur est anonyme (non authentifié)
        scope["user"] = AnonymousUser()

        if token:
            try:
                # Valider la signature et l'expiration du token JWT
                validated_token = JWTAuthentication().get_validated_token(token)
                # Récupérer l'objet User correspondant au token validé
                user = JWTAuthentication().get_user(validated_token)
                scope["user"] = user
            except Exception:
                # Token invalide, expiré ou utilisateur supprimé — on garde AnonymousUser
                pass

        return await self.app(scope, receive, send)