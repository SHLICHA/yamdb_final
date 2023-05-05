from datetime import datetime

from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from users.models import User


class Category(models.Model):
    """Класс категорий."""

    name = models.CharField(
        max_length=256,
        verbose_name="Название категории",
        db_index=True,  # индекс нужен для ускорения поиска по имени
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name="slug",
        unique=True,
        validators=[
            RegexValidator(  # валидатор для regex фильтра в слаге
                regex=r"^[-a-zA-Z0-9_]+$",
                message="Слаг категории содержит недопустимый символ",
            )
        ],
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Категория"

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Класс жанров."""

    name = models.CharField(
        max_length=256,
        verbose_name="Название жанра",
        db_index=True,
    )
    slug = models.SlugField(
        max_length=50,
        verbose_name="slug",
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[-a-zA-Z0-9_]+$",
                message="Слаг категории содержит недопустимый символ",
            )
        ],
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Жанр"

    def __str__(self):
        return self.name


class Title(models.Model):
    """Класс произведений."""

    name = models.CharField(
        max_length=256,
        verbose_name="Название произведения",
        db_index=True,
    )
    year = models.PositiveIntegerField(
        verbose_name="Год выпуска",
        validators=[
            MinValueValidator(
                0, message="Значение года не может быть отрицательным"
            ),
            MaxValueValidator(
                int(datetime.now().year),
                message="Значение года не может быть больше текущего",
            ),
        ],
        db_index=True,
    )
    description = models.CharField(
        max_length=1000,
        verbose_name="Описание произведения",
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre,
        through="GenreTitle",
        verbose_name="Жанр",
        related_name="titles",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="titles",
        null=True,
        verbose_name="Категория",
    )

    class Meta:
        ordering = ("-year", "name")
        verbose_name = "Произведение"

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Вспомогательный класс, связывающий жанры и произведения."""

    genre = models.ForeignKey(
        Genre, on_delete=models.CASCADE, verbose_name="Жанр"
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, verbose_name="произведение"
    )

    class Meta:
        verbose_name = "Соответствие жанра и произведения"
        verbose_name_plural = "Таблица соответствия жанров и произведений"
        ordering = ("id",)

    def __str__(self):
        return f"{self.title} принадлежит жанру/ам {self.genre}"


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        verbose_name="Произведение",
        on_delete=models.CASCADE,
        related_name="reviews",
        null=True,
    )
    text = models.TextField(
        verbose_name="Текст",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    score = models.PositiveSmallIntegerField(
        verbose_name="Рейтинг",
        validators=[
            MinValueValidator(1, "Допустимы значения от 1 до 10"),
            MaxValueValidator(10, "Допустимы значения от 1 до 10"),
        ],
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации", auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ("-pub_date",)
        constraints = [
            models.UniqueConstraint(
                fields=["title", "author"], name="unique_review"
            ),
        ]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        verbose_name="Отзыв",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    text = models.TextField(
        verbose_name="Текст",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата публикации", auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ("-pub_date",)
