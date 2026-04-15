from rest_framework import generics
from drf_spectacular.utils import extend_schema
from .models import User
from .serializers import UserSerializer


class UserCreateView(generics.CreateAPIView):
    """
    Crée un nouveau compte utilisateur (inscription).

    Endpoint public — aucune authentification requise.
    Le rôle doit être fourni lors de la création (client, courier ou admin).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @extend_schema(
        summary="Créer un compte utilisateur",
        description=(
            "Inscription d'un nouvel utilisateur. "
            "Le champ `role` doit être l'un des suivants : `client`, `courier`, `admin`. "
            "Le numéro de téléphone doit être unique."
        ),
        tags=["Authentification"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserListView(generics.ListAPIView):
    """
    Liste tous les utilisateurs enregistrés.

    Endpoint réservé aux administrateurs dans un contexte de production.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @extend_schema(
        summary="Lister tous les utilisateurs",
        description="Retourne la liste complète des utilisateurs. "
                    "À restreindre aux administrateurs en production.",
        tags=["Authentification"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
