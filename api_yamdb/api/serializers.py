from django.contrib.auth.tokens import default_token_generator
from django.core.validators import MaxLengthValidator, RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        slug_field="username",
        read_only=True,
    )

    def validate(self, data):
        request = self.context["request"]
        author = request.user
        title_id = self.context["view"].kwargs.get("title_id")
        if request.method == "POST":
            if Review.objects.filter(
                title_id=title_id, author=author
            ).exists():
                raise ValidationError(
                    "Вы не можете добавить более"
                    "одного отзыва на произведение"
                )
        return data

    class Meta:
        model = Review
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.SlugRelatedField(slug_field="text", read_only=True)
    author = serializers.SlugRelatedField(
        slug_field="username", read_only=True
    )

    class Meta:
        model = Comment
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        exclude = ("id",)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        model = Genre
        exclude = ("id",)


class TitleGETSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Title при GET запросах."""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "rating",
            "description",
            "genre",
            "category",
        )


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title."""

    genre = serializers.SlugRelatedField(
        slug_field="slug", queryset=Genre.objects.all(), many=True
    )
    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            "id",
            "name",
            "year",
            "description",
            "genre",
            "category",
        )

    def to_representation(self, title):
        """Определяет какой сериализатор будет использоваться для чтения."""
        serializer = TitleGETSerializer(title)
        return serializer.data


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+$",
                message="Некорректный логин",
            ),
            MaxLengthValidator(150, "Логин слишком длинный"),
            UniqueValidator(queryset=User.objects.all()),
        ]
    )
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            MaxLengthValidator(254, "Адрес слишком длинный"),
        ]
    )

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.first_name = validated_data.get(
            "first_name", instance.first_name
        )
        instance.last_name = validated_data.get(
            "last_name", instance.last_name
        )
        instance.bio = validated_data.get("bio", instance.bio)
        instance.save()
        return instance

    def validate(self, data):
        if data.get("username") == "me":
            raise serializers.ValidationError("Запрещенный логин")
        if User.objects.filter(username=data.get("username")):
            raise serializers.ValidationError(
                "Пользователь с таким username уже существует"
            )
        if User.objects.filter(email=data.get("email")):
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует"
            )
        return data

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )


class GetTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+$",
                message="Некорректный логин",
            ),
            MaxLengthValidator(150, "Логин слишком длинный"),
        ],
    )
    confirmation_code = serializers.SerializerMethodField()

    def get_confirmation_code(self, obj):
        user = User.objects.get(username=obj.username)
        return default_token_generator.make_token(user)

    def validate(self, data):
        errors = []
        if "username" not in data:
            errors.append("Введите имя пользователя")
        if "confirmation_code" not in data:
            errors.append("Введите код")
        if not User.objects.filter(username=data.get("username")).exists():
            errors.append("Несуществующий пользователь")
        user = get_object_or_404(User, username=data.get("username"))
        confirmation_code = data.get("confirmation_code")
        if default_token_generator.check_token(user, confirmation_code):
            errors.append("Неверный код")
        if errors:
            raise serializers.ValidationError(errors)
        return data

    class Meta:
        model = User
        fields = (
            "username",
            "confirmation_code",
        )
