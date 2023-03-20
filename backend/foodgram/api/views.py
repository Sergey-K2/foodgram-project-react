from django.shortcuts import get_object_or_404
from rest_framework import mixins
from rest_framework.viewsets import (
    ModelViewSet,
    ReadOnlyModelViewSet,
    GenericViewSet,
)

from .permissions import AuthenticatedOrAuthorOrReadOnly
from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    Subscription,
    ShoppingCard,
    Favorite,
    Users,
)
from .serializers import (
    RecipeSerializer,
    TagSerializer,
    IngredientSerializer,
    SubscriptionSerializer,
    ShoppingCardSerializer,
    FavoriteSerializer,
)


class ListRetrieveViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet
):
    pass


class ListCreateDestroyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    pass


class CreateDeleteViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet
):
    pass


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class SubscriptionViewSet(ListCreateDestroyViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer


class ShoppingCardViewSet(ListCreateDestroyViewSet):
    queryset = ShoppingCard.objects.all()
    serializer_class = ShoppingCardSerializer


class FavoriteViewSet(CreateDeleteViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
