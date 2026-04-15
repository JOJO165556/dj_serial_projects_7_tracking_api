from django.db import models
from django.conf import settings

# Référence au modèle User configuré dans les settings (AUTH_USER_MODEL)
User = settings.AUTH_USER_MODEL


class CourierProfile(models.Model):
    """
    Profil étendu d'un livreur, lié à son compte utilisateur.

    Stocke la position GPS actuelle du livreur et son statut de disponibilité.
    Ce modèle est utilisé pour l'algorithme d'assignation automatique des colis.
    """

    # Relation 1-1 avec l'utilisateur — chaque livreur a exactement un profil
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="courier_profile"
    )

    # Coordonnées GPS actuelles du livreur (mises à jour lors des déplacements)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    # Indique si le livreur peut accepter une nouvelle livraison
    is_available = models.BooleanField(default=True)

    # Horodatage mis à jour automatiquement à chaque modification du profil
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} (Courier)"
