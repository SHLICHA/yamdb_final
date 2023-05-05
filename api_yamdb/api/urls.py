from api.views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    get_code,
    get_token,
    ReviewViewSet,
    TitleViewSet,
    UserViewSet)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewViewSet, basename="reviews"
)
router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)" r"/comments",
    CommentViewSet,
    basename="comments",
)
router.register("users", UserViewSet, basename="users")
router.register("categories", CategoryViewSet, basename="categories")
router.register("genres", GenreViewSet, basename="genres")
router.register("titles", TitleViewSet, basename="titles")

auth_urls = [
    path("signup/", get_code),
    path("token/", get_token),
]

urlpatterns = [
    path("v1/auth/", include(auth_urls)),
    path("v1/", include(router.urls)),
]
