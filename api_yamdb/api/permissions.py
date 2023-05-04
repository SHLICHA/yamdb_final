from rest_framework import permissions


class AdminOnly(permissions.BasePermission):
    """Запрет любых действий всем, кроме пользователя
    с ролью администратор"""

    message = "Доступно только администратору"

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_admin or request.user.is_staff
        return False

    def has_object_permission(self, request, view, obj):
        return request.user.is_admin or request.user.is_staff


class IsAdminModeratorOwnerOrReadOnly(permissions.BasePermission):
    """Доступ только пользователям с ролями администратор и модератор"""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
            or request.user.is_moderator
            or request.user == obj.author
        )


class IsUserOwner(permissions.BasePermission):
    """Доступ только автору"""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (request.user.is_authenticated
                and obj.author == request.user
                )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Доступ только администратору, остальным только чтение"""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_admin
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return request.user.is_admin
        return False


class AnonimReadOnly(permissions.BasePermission):
    """Разрешает анонимному пользователю только безопасные запросы."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
