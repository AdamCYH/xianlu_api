from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class ClientPermission(permissions.BasePermission):
    group_name = "client"

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS or request.user and request.user.is_authenticated():
            return True
        return False


class AdminPermission(permissions.BasePermission):
    group_name = "admin"

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user


class IsUserSelf(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user_id == request.user.user_id


class IsUserSelfOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.user_id or request.user.is_staff
