from rest_framework import permissions
from users.models import ROLE_CHOICES


class OwnerAdminOrReadOnly(permissions.BasePermission):
    """Manage permissions.
    SAFE methods allowed for anyone.
    `POST` allowed for authenticated users.
    Other methods allowed for object author, moderator or admin.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            obj.author == request.user
            or request.user.role in [ROLE_CHOICES.ADMIN]
            or request.user.is_superuser)


class IsAdmin(permissions.IsAuthenticated):
    """Access for admin or superuser."""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and (
            request.user.role == (
                ROLE_CHOICES.ADMIN or request.user.is_superuser)
        )


class IsAdminOrReadOnly(IsAdmin):
    """Manage permissions.
    SAFE methods allowed for anyone,
    inlcuding not authenticateed.
    `POST` allowed for admin.
    Other methods allowed for admin.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or super().has_permission(request, view))


class AdminOrViewOrCreateOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            return True
        return (request.user.is_superuser
                or request.user.role in [ROLE_CHOICES.ADMIN])

    def has_object_permission(self, request, view, obj):
        if request.method == 'GET' and request.user.is_authenticated:
            return super().has_object_permission(request, view, obj)
        return False
