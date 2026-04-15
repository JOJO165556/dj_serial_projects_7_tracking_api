from rest_framework.permissions import BasePermission


class IsClient(BasePermission):
    """
    Autorise l'accès uniquement aux utilisateurs ayant le rôle 'client'.

    Utilisé sur les vues de création et de consultation de colis.
    """
    def has_permission(self, request, view):
        return request.user.role == "client"


class IsCourier(BasePermission):
    """
    Autorise l'accès uniquement aux utilisateurs ayant le rôle 'courier'.

    Utilisé sur les vues de mise à jour de statut et de position GPS.
    """
    def has_permission(self, request, view):
        return request.user.role == "courier"


class IsAdmin(BasePermission):
    """
    Autorise l'accès uniquement aux utilisateurs ayant le rôle 'admin'.

    Utilisé sur les vues d'assignation de livreur et de consultation analytics.
    """
    def has_permission(self, request, view):
        return request.user.role == "admin"


class IsParcelOwner(BasePermission):
    """
    Permission au niveau objet — autorise uniquement l'expéditeur du colis.

    Vérifie que l'utilisateur connecté est le sender du colis.
    Doit être appelée via check_object_permissions() dans la vue.
    """
    def has_object_permission(self, request, view, obj):
        return obj.sender == request.user


class IsAssignedCourier(BasePermission):
    """
    Permission au niveau objet — autorise uniquement le livreur assigné au colis.

    Vérifie que le colis a un livreur assigné et que c'est bien l'utilisateur connecté.
    Doit être appelée via check_object_permissions() dans la vue.
    """
    def has_object_permission(self, request, view, obj):
        # Vérifier qu'un livreur est assigné avant de comparer l'utilisateur
        return obj.assigned_courier is not None and obj.assigned_courier.user == request.user