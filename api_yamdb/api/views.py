from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title
from users.models import User

from .filters import TitleFilter
from .mixins import CreateListDestroyViewSet
from .permissions import (AdminOnly, AnonimReadOnly,
                          IsAdminModeratorOwnerOrReadOnly, IsAdminOrReadOnly,
                          IsUserOwner)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetTokenSerializer,
                          ReviewSerializer, TitleGETSerializer,
                          TitleSerializer, UserSerializer)
from .utils import mail_send


@api_view(["POST"])
@permission_classes([AllowAny])
def get_code(request):
    """Создание пользователя, используя api/v1/auth/singup.
    Отправка email и username. Далее пользователю на указанный email приходит
    письмо с confirmation_code для последующей авторизации и получения
    токена"""
    if User.objects.filter(username=request.data.get("username")).exists():
        user = User.objects.get(username=request.data.get("username"))
        confirmation_code = default_token_generator.make_token(user)
        if user.email != request.data.get("email"):
            return Response(
                "Неверный Email", status=status.HTTP_400_BAD_REQUEST
            )
        mail_send(user.email, confirmation_code)
        return Response(confirmation_code, status=status.HTTP_200_OK)
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    user = get_object_or_404(
        User, username=serializer.validated_data["username"]
    )
    confirmation_code = default_token_generator.make_token(user)
    mail_send(user.email, confirmation_code)
    return Response(serializer.validated_data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes(
    [
        AllowAny,
    ]
)
def get_token(request):
    """Отправка JWT-токена пользователю по полям
    username и confirmation_code"""
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data["username"]
    user = User.objects.get(username=username)
    token = RefreshToken.for_user(user)
    message = {
        "refresh": str(token),
        "access": str(token.access_token),
    }
    return Response(message, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """Работа администратора с данными пользователей.
    Создание, изменение, удаление. Ссылка ../users/{username}/ - страница
    пользователя для работы. На вход приходит username пользователя.
    ../users/ - получение списка пользователей"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    permission_classes = (AdminOnly,)
    http_method_names = ["get", "post", "patch", "delete"]

    def perform_create(self, serializer):
        """Создание пользователя"""
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.validated_data, status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, pk=None):
        """Получение пользователя"""
        queryset = User.objects.filter(username=pk)
        user = get_object_or_404(queryset)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def destroy(self, request, pk):
        """Удаление пользователя"""
        queryset = User.objects.filter(username=pk)
        user = get_object_or_404(queryset)
        user.delete()
        return Response(
            "Пользователь удален", status=status.HTTP_204_NO_CONTENT
        )

    def partial_update(self, request, pk):
        """Изменение данных пользователя"""
        queryset = User.objects.filter(username=pk)
        user = get_object_or_404(queryset)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(
                "Некорректные данные", status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.validated_data)

    @action(
        methods=["get", "patch"],
        detail=False,
        url_path="me",
        permission_classes=[IsUserOwner],
    )
    def me(self, request):
        """Получение собственных данных"""
        serializer = UserSerializer(request.user)
        if request.method == "GET":
            return Response(serializer.data)
        pk = request.user.pk
        user = User.objects.get(id=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(
                "Некорректные данные", status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.validated_data)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminModeratorOwnerOrReadOnly]

    def get_title(self):
        """Возвращает объект текущего произведения."""
        title_id = self.kwargs.get("title_id")
        return get_object_or_404(Title, pk=title_id)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get("title_id"))
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get("title_id")
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAdminModeratorOwnerOrReadOnly]

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get("review_id"))
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get("title_id")
        review_id = self.kwargs.get("review_id")
        review = get_object_or_404(Review, id=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)


class CategoryViewSet(CreateListDestroyViewSet):
    """Вьюсет для создания обьектов класса Category."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class GenreViewSet(CreateListDestroyViewSet):
    """Вьюсет для создания обьектов класса Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для создания обьектов класса Title."""

    queryset = Title.objects.annotate(rating=Avg("reviews__score"))
    serializer_class = TitleSerializer
    permission_classes = [IsAdminOrReadOnly | AnonimReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        """Определяет какой сериализатор будет использоваться
        для разных типов запроса."""
        if self.request.method == "GET":
            return TitleGETSerializer
        return TitleSerializer
