from django.contrib import admin

from .models import Category, Comment, Genre, GenreTitle, Title, Review

admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(GenreTitle)
admin.site.register(Title)
admin.site.register(Review)
admin.site.register(Comment)
