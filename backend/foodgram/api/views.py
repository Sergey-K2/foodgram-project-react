from django.shortcuts import get_object_or_404
from rest_framework import filters
from rest_framework import mixins
from rest_framework.viewsets import (
    ModelViewSet,
    ReadOnlyModelViewSet,
    GenericViewSet,
)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
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
    permission_classes = (AuthenticatedOrAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class SubscriptionViewSet(ListCreateDestroyViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("following__username", "user__username")
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return self.request.user.follower.all()


class ShoppingCardViewSet(ListCreateDestroyViewSet):
    serializer_class = ShoppingCardSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self):
        pass

    def get_queryset(self):
        pass


class FavoriteViewSet(CreateDeleteViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitOffsetPagination

    def perform_create(self):
        pass

    def get_queryset(self):
        pass
