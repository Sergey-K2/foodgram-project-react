from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                    UsersSubscriptionViewSet)

app_name = "api"

v1_router = DefaultRouter()

v1_router.register("recipes", RecipeViewSet)
v1_router.register("tags", TagViewSet)
v1_router.register("ingredients", IngredientViewSet)
v1_router.register("users", UsersSubscriptionViewSet, basename="subscriptions")

urlpatterns = [
    path("", include(v1_router.urls)),
    path("", include("djoser.urls")),
    path("auth/token/login/", TokenCreateView.as_view(), name="login"),
    path("auth/token/logout/", TokenDestroyView.as_view(), name="logout"),
]
