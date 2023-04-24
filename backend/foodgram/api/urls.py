from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, SubscriptionViewSet,
                    TagViewSet)

app_name = "api"

v1_router = DefaultRouter()

v1_router.register("recipes", RecipeViewSet)
v1_router.register("tag", TagViewSet)
v1_router.register("ingredients", IngredientViewSet)
v1_router.register(
    "subscriptions", SubscriptionViewSet, basename="subscriptions"
)

urlpatterns = [
    path("", include(v1_router.urls)),
    path("auth/", include("djoser.urls")),
]
