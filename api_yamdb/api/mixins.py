from rest_framework import filters, mixins, viewsets

from .permissions import IsAdminModeratorOwnerOrReadOnly


class CreateListDestroyViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Вьюсет, позволяющий осуществлять GET, POST и DELETE запросы.
    Поддерживает обработку адреса с динамической переменной slug."""

    permission_classes = IsAdminModeratorOwnerOrReadOnly
    filter_backends = (filters.SearchFilter,)  # not forget to fix it
    search_fields = ("name",)
    lookup_field = "slug"
