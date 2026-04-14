from rest_framework.permissions import BasePermission

class IsClient(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "client"

class IsCourier(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "courier"

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "admin"

class IsParcelOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.sender == request.user

class IsAssignedCourier(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.assigned_courier is not None and obj.assigned_courier.user == request.user