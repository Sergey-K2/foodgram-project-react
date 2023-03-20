from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    RecipeViewSet,
    TagViewSet,
    IngredientViewSet,
    SubscriptionViewSet,
    FavoriteViewSet,
    ShoppingCardViewSet,
)

app_name = "api"

v1_router = DefaultRouter()

v1_router.register("recipes", RecipeViewSet, basename="recipes")
v1_router.register(
    r"recipes/(?P<recipe_id>\d+)/favorites",
    FavoriteViewSet,
    basename="favorites",
)
v1_router.register(
    r"recipes/(?P<recipe_id>\d+)/favorites",
    ShoppingCardViewSet,
    basename="shopping_cart",
)
v1_router.register("tag", TagViewSet, basename="tags")
v1_router.register("ingredients", IngredientViewSet, basename="tags")
v1_router.register(
    "subscriptions", SubscriptionViewSet, basename="subscriptions"
)

urlpatterns = [
    path("v1/", include(v1_router.urls)),
    path("auth/", include("djoser.urls")),
    path("v1/", include("djoser.urls.jwt")),
]
