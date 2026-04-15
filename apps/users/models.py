from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé de l'application.

    Étend AbstractUser en ajoutant un numéro de téléphone unique
    et un rôle qui détermine les droits d'accès à l'API.
    Le rôle est utilisé par les classes de permission (IsClient, IsCourier, IsAdmin).
    """

    class Role(models.TextChoices):
        """Rôles possibles dans le système."""
        CLIENT = "client", "Client"      # Utilisateur qui envoie des colis
        COURIER = "courier", "Courier"   # Livreur qui transporte les colis
        ADMIN = "admin", "Admin"         # Administrateur avec accès total

    # Numéro de téléphone unique — utilisé pour identifier et contacter l'utilisateur
    phone = models.CharField(max_length=20, unique=True)

    # Rôle de l'utilisateur — conditionne ses droits sur les endpoints de l'API
    role = models.CharField(max_length=20, choices=Role.choices)  # type: ignore

    def __str__(self):
        return f"{self.username} ({self.role})"
